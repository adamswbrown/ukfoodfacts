"""
Grill'd Australia nutrition scraper.
Grill'd is a Melbourne-founded healthy burger chain (180+ outlets across Australia).
Nutrition data is served via Contentful CMS and rendered client-side in a Vue/Nuxt app,
so live scraping requires parsing the Contentful JSON payload from the page source.
"""

import json
import re
import requests
from datetime import date

from scrapers.dietary_utils import infer_dietary_flags

SOURCE_URL = "https://grilld.com.au/nutrition"
MENU_URL = "https://grilld.com.au/menu"
ALLERGEN_PDF_URL = "https://images.ctfassets.net/quhz534suzyl/46qL9C8WCu58UIgOc3ZOOX/1e5973a28dcef66e2d506ac2d18c56b9/Allergen_Matrix_National_v12_Dec_2025.pdf"

# Known menu item slugs and their categories
MENU_ITEMS = {
    "Burgers": [
        "simply-grilld", "the-mighty", "hfc-classic", "hfc-blat",
        "baa-baa", "simon-says", "zen-hen", "crispy-bacon-cheeseburger",
        "summer-crispy-chicken", "garden-goodness",
    ],
    "Salads": [
        "mighty-caesar", "super-green",
    ],
    "Sliders": [
        "simply-grilld-slider", "hfc-slider",
    ],
    "Sides": [
        "famous-grilld-chips", "hfc-bites", "sweet-potato-chips",
    ],
    "Kids": [
        "mini-me-beef", "mini-me-chicken",
    ],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape():
    print("  [GrilldAU] Attempting live scrape...")
    try:
        items = _scrape_menu_items()
        if items:
            print(f"  [GrilldAU] Scraped {len(items)} items from website")
            return items
    except Exception as e:
        print(f"  [GrilldAU] Live scrape failed: {e}")

    print("  [GrilldAU] Using fallback data")
    return _fallback_data()


def _scrape_menu_items():
    """Try to extract nutrition data from individual menu item pages."""
    today = str(date.today())
    items = []

    for category, slugs in MENU_ITEMS.items():
        for slug in slugs:
            url = f"https://grilld.com.au/menu/{slug}"
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                if resp.status_code != 200:
                    continue
                parsed = _parse_item_page(resp.text, category, today)
                if parsed:
                    items.extend(parsed)
            except Exception:
                continue

    return items


def _parse_item_page(html, category, today):
    """
    Parse a Grill'd menu item page. The page is a Vue/Nuxt app that embeds
    Contentful data as JSON in a <script> tag. Look for nutrition data in
    the embedded JSON or in structured data.
    """
    items = []

    # Try to find the item name from the page
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html)
    if not title_match:
        return items
    raw_title = title_match.group(1)
    # Clean title: remove " | Grill'd Healthy Burgers" suffix
    name = re.sub(r'\s*\|.*$', '', raw_title).strip()
    name = name.strip("'\"")
    if not name or name.lower() in ("menu", "grill'd", "grilld"):
        return items

    # Try to extract nutrition from Contentful JSON payload
    # Look for JSON objects containing nutrition-related fields
    nutrition = _extract_nutrition_from_json(html)

    if nutrition:
        for variant_name, data in nutrition.items():
            display_name = f"{name} ({variant_name})" if variant_name else name
            items.append(_build_item(display_name, category, data, today))
    else:
        # No nutrition data found in this page
        return items

    return items


def _extract_nutrition_from_json(html):
    """
    Search for nutrition data in embedded JSON.
    Grill'd uses Contentful CMS; the data may be in __NUXT_DATA__ or similar.
    """
    results = {}

    # Look for patterns like "Energy" "Protein" "Fat" near numeric values
    # in JSON-like structures
    json_blocks = re.findall(r'<script[^>]*>\s*(?:window\.__NUXT(?:_DATA)?__\s*=\s*)?(\{.+?\})\s*</script>', html, re.DOTALL)

    for block in json_blocks:
        try:
            data = json.loads(block)
            _search_nutrition_in_obj(data, results)
        except (json.JSONDecodeError, ValueError):
            continue

    return results


def _search_nutrition_in_obj(obj, results, depth=0):
    """Recursively search a JSON object for nutrition data."""
    if depth > 10:
        return
    if isinstance(obj, dict):
        # Check if this dict has nutrition-like keys
        keys_lower = {str(k).lower() for k in obj.keys()}
        if 'energy' in keys_lower or 'calories' in keys_lower or 'protein' in keys_lower:
            energy = obj.get('energy') or obj.get('Energy') or obj.get('calories') or obj.get('Calories')
            protein = obj.get('protein') or obj.get('Protein')
            if energy and protein:
                variant = obj.get('name', obj.get('title', ''))
                results[variant] = obj
                return
        for v in obj.values():
            _search_nutrition_in_obj(v, results, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            _search_nutrition_in_obj(item, results, depth + 1)


def _build_item(name, category, data, today):
    """Build a standardised item dict from parsed nutrition data."""
    # Try to extract values, handling both kJ and kcal
    energy = _safe_float(data.get('energy') or data.get('Energy') or data.get('calories') or data.get('Calories'))
    energy_unit = str(data.get('energyUnit', data.get('unit', 'kJ'))).lower()

    if energy and 'kj' in energy_unit:
        calories = round(energy / 4.184)
    else:
        calories = _safe_int(energy)

    return {
        "restaurant": "Grill'd",
        "category": category,
        "item": name,
        "description": "",
        "calories_kcal": calories,
        "protein_g": _safe_float(data.get('protein') or data.get('Protein')),
        "carbs_g": _safe_float(data.get('carbohydrate') or data.get('Carbohydrate') or data.get('carbs')),
        "fat_g": _safe_float(data.get('fat') or data.get('Fat') or data.get('totalFat')),
        "fibre_g": _safe_float(data.get('fibre') or data.get('Fibre') or data.get('dietaryFibre')),
        "salt_g": _sodium_to_salt(data.get('sodium') or data.get('Sodium')),
        "allergens": [],
        "dietary_flags": infer_dietary_flags(name),
        "source_url": SOURCE_URL,
        "location": "National",
        "scraped_at": today,
    }


def _sodium_to_salt(sodium_val):
    """Convert sodium (mg) to salt (g)."""
    sodium = _safe_float(sodium_val)
    if sodium is not None:
        return round(sodium * 2.5 / 1000, 1)
    return None


def _safe_int(val):
    if val is None:
        return None
    try:
        return int(float(str(val).replace(",", "").strip()))
    except (ValueError, TypeError):
        return None


def _safe_float(val):
    if val is None:
        return None
    try:
        return round(float(str(val).replace(",", "").replace("g", "").replace("mg", "").strip()), 1)
    except (ValueError, TypeError):
        return None


def _fallback_data():
    """
    Hardcoded seed data for Grill'd burgers.
    Sources: Grill'd website, CalorieKing AU, MyNetDiary, Carb Manager.
    All values are for Traditional Bun unless noted.
    """
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, fibre, salt_g, allergens, description
        ("Burgers", "Simply Grill'd", 550, 32.0, 47.0, 25.0, 3.0, 2.4,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Grass-fed beef patty w/ cos lettuce, tomato, Spanish onion, relish & herbed mayo"),
        ("Burgers", "The Mighty", 715, 36.0, 44.0, 39.4, 3.5, 3.1,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Beef patty w/ crispy bacon, egg, tasty cheese, beetroot, cos lettuce, tomato, onion, relish & herbed mayo"),
        ("Burgers", "HFC Classic", 590, 38.0, 51.0, 24.0, 2.5, 2.8,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "RSPCA Approved crispy fried chicken w/ cos lettuce, herbed mayo"),
        ("Burgers", "HFC BLAT", 621, 32.0, 51.0, 31.0, 3.0, 3.2,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Crispy fried chicken w/ crispy bacon, cos lettuce, avocado, tomato & herbed mayo"),
        ("Burgers", "Baa Baa", 620, 35.0, 43.0, 33.0, 3.0, 2.9,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Australian lamb patty w/ tasty cheese, cos lettuce, tomato, beetroot, relish & herbed mayo"),
        ("Burgers", "Simon Says", 580, 34.0, 45.0, 28.0, 3.5, 2.7,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic", "sesame"],
         "Beef patty w/ tasty cheese, cos lettuce, tomato, pickles, Simon Says sauce"),
        ("Burgers", "Zen Hen", 530, 42.0, 40.0, 21.0, 3.0, 2.5,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Grilled chicken breast w/ avocado, cos lettuce, tomato, Spanish onion & herbed mayo"),
        ("Burgers", "Crispy Bacon & Cheese", 680, 38.0, 46.0, 37.0, 2.5, 3.4,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Beef patty w/ crispy bacon, tasty cheese, cos lettuce, tomato, pickles & mustard mayo"),
        ("Burgers", "Garden Goodness", 480, 18.0, 52.0, 22.0, 6.0, 2.1,
         ["gluten", "soy", "onion", "garlic"],
         "Plant-based patty w/ cos lettuce, tomato, Spanish onion, relish & herbed mayo"),
        ("Burgers", "Dynamic Chicken", 533, 46.0, 39.0, 20.0, 2.5, 2.3,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Grilled chicken w/ tasty cheese, cos lettuce, tomato & herbed mayo"),
        ("Salads", "Mighty Caesar Salad", 420, 28.0, 18.0, 28.0, 4.0, 2.0,
         ["egg", "dairy", "fish", "garlic"],
         "Grilled chicken, cos lettuce, parmesan, croutons & caesar dressing"),
        ("Salads", "Super Green Salad", 350, 30.0, 12.0, 20.0, 5.0, 1.5,
         ["egg", "dairy", "garlic"],
         "Grilled chicken, mixed greens, avocado, broccolini & lemon dressing"),
        ("Sliders", "Simply Grill'd Slider", 290, 16.0, 24.0, 13.0, 1.5, 1.2,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Mini beef patty w/ cos lettuce, tomato, relish & herbed mayo"),
        ("Sliders", "HFC Slider", 310, 19.0, 26.0, 12.0, 1.5, 1.4,
         ["gluten", "egg", "dairy", "soy", "onion", "garlic"],
         "Mini crispy fried chicken w/ cos lettuce & herbed mayo"),
        ("Sides", "Famous Grill'd Chips", 390, 5.0, 52.0, 18.0, 4.0, 1.2,
         ["soy"], "Skin-on chips cooked in extra virgin olive oil"),
        ("Sides", "Sweet Potato Chips", 350, 4.0, 48.0, 16.0, 5.0, 1.0,
         ["soy"], "Sweet potato chips cooked in extra virgin olive oil"),
        ("Sides", "HFC Bites (6 pack)", 320, 24.0, 18.0, 16.0, 1.0, 1.6,
         ["gluten", "egg", "soy"],
         "RSPCA Approved crispy chicken bites cooked in extra virgin olive oil"),
        ("Kids", "Mini Me Beef Burger", 380, 22.0, 32.0, 18.0, 2.0, 1.5,
         ["gluten", "egg", "dairy", "soy"],
         "Beef patty w/ tasty cheese, cos lettuce & tomato sauce"),
        ("Kids", "Mini Me Chicken Burger", 350, 26.0, 30.0, 14.0, 2.0, 1.4,
         ["gluten", "egg", "dairy", "soy"],
         "Grilled chicken w/ cos lettuce & herbed mayo"),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, fibre, salt, allergens, desc in raw:
        items.append({
            "restaurant": "Grill'd",
            "category": cat,
            "item": name,
            "description": desc,
            "calories_kcal": kcal,
            "protein_g": prot,
            "carbs_g": carbs,
            "fat_g": fat,
            "fibre_g": fibre,
            "salt_g": salt,
            "allergens": allergens,
            "dietary_flags": infer_dietary_flags(name, desc),
            "source_url": SOURCE_URL,
            "location": "National",
            "scraped_at": today,
        })
    print(f"  [GrilldAU] Using {len(items)} fallback items")
    return items
