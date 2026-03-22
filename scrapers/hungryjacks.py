"""
Hungry Jack's Australia nutrition scraper.
Scrapes JSON-LD schema.org data from menu category pages on hungryjacks.com.au.
Each category page embeds MenuItems with NutritionInformation (energy in kJ,
sodium in mg) which we convert to kcal and salt_g respectively.
"""

import json
import re
from datetime import date

import requests

from scrapers.dietary_utils import infer_dietary_flags

BASE_URL = "https://www.hungryjacks.com.au"
SOURCE_URL = "https://www.hungryjacks.com.au/menu"

# Menu category slugs and the display category name to assign
CATEGORY_PAGES = [
    ("whopper", "Whopper & Beef"),
    ("chicken-burgers", "Chicken Burgers"),
    ("angus-grill-masters", "Grill Masters"),
    ("chicken-sides", "Chicken & Tenders"),
    ("veggie-range", "Veggie"),
    ("sides-snacks", "Sides & Snacks"),
    ("breakfast", "Breakfast"),
    ("desserts", "Desserts"),
    ("kids", "Kids"),
    ("penny-pinchers", "Penny Pinchers"),
    ("bundle-meals", "Bundle Meals"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HobbyNutritionBot/1.0; personal use)",
}

# kJ to kcal conversion factor
KJ_TO_KCAL = 0.239006


def scrape():
    print("  [HungryJacks] Scraping JSON-LD from menu pages...")
    try:
        items = _scrape_all_categories()
        if items:
            print(f"  [HungryJacks] Scraped {len(items)} items from JSON-LD")
            return items
    except Exception as e:
        print(f"  [HungryJacks] Scrape failed: {e}")

    print("  [HungryJacks] Using fallback data")
    return _fallback_data()


def _scrape_all_categories():
    """Fetch each category page and extract JSON-LD MenuItems."""
    today = str(date.today())
    all_items = []
    seen = set()

    for slug, category in CATEGORY_PAGES:
        url = f"{BASE_URL}/menu/{slug}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            page_items = _extract_jsonld_items(resp.text, category, url, today)
            for item in page_items:
                key = item["item"]
                if key not in seen:
                    seen.add(key)
                    all_items.append(item)
            if page_items:
                print(f"    {category}: {len(page_items)} items")
        except Exception as e:
            print(f"    {category}: failed ({e})")

    return all_items


def _extract_jsonld_items(html, category, page_url, today):
    """Parse JSON-LD script tags and extract MenuItems with nutrition data."""
    items = []
    # Find all JSON-LD blocks
    pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    matches = re.findall(pattern, html, re.DOTALL)

    for raw in matches:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        # JSON-LD can be a single object or a list
        if isinstance(data, list):
            for obj in data:
                _process_jsonld_object(obj, category, page_url, today, items)
        else:
            _process_jsonld_object(data, category, page_url, today, items)

    return items


def _process_jsonld_object(obj, category, page_url, today, items):
    """Process a JSON-LD object, looking for Menu or MenuItem types."""
    obj_type = obj.get("@type", "")

    if obj_type == "Menu":
        # Menu contains hasMenuSection with MenuItem entries
        sections = obj.get("hasMenuSection", [])
        if isinstance(sections, dict):
            sections = [sections]
        for section in sections:
            menu_items = section.get("hasMenuItem", [])
            if isinstance(menu_items, dict):
                menu_items = [menu_items]
            for mi in menu_items:
                item = _parse_menu_item(mi, category, page_url, today)
                if item:
                    items.append(item)

    elif obj_type == "MenuItem":
        item = _parse_menu_item(obj, category, page_url, today)
        if item:
            items.append(item)


def _parse_menu_item(mi, category, page_url, today):
    """Convert a schema.org MenuItem dict into our standard item dict."""
    name = mi.get("name", "").strip()
    if not name:
        return None

    description = mi.get("description", "") or ""
    nutrition = mi.get("nutrition", {})
    if not nutrition:
        return None

    # Energy is in kJ, convert to kcal
    energy_kj = _safe_float(nutrition.get("calories", ""))
    calories_kcal = round(energy_kj * KJ_TO_KCAL) if energy_kj is not None else None

    protein = _safe_float(nutrition.get("proteinContent", ""))
    fat = _safe_float(nutrition.get("fatContent", ""))
    carbs = _safe_float(nutrition.get("carbohydrateContent", ""))

    # Sodium is in mg, convert to salt g (salt = sodium * 2.5 / 1000)
    sodium_mg = _safe_float(nutrition.get("sodiumContent", ""))
    salt_g = round(sodium_mg * 2.5 / 1000, 1) if sodium_mg is not None else None

    # Skip items with no meaningful nutrition data
    if calories_kcal is None and protein is None:
        return None

    return {
        "restaurant": "Hungry Jacks",
        "category": category,
        "item": name,
        "description": description.strip(),
        "calories_kcal": calories_kcal,
        "protein_g": protein,
        "carbs_g": carbs,
        "fat_g": fat,
        "fibre_g": None,  # not in JSON-LD schema
        "salt_g": salt_g,
        "allergens": [],  # not available in JSON-LD; would need PDFs
        "dietary_flags": infer_dietary_flags(name, description),
        "source_url": page_url,
        "scraped_at": today,
    }


def _safe_int(val):
    """Convert a value to int, returning None on failure."""
    if val is None or val == "":
        return None
    try:
        cleaned = str(val).replace(",", "").replace("~", "").strip()
        cleaned = re.sub(r'[^\d.\-]', '', cleaned)
        return int(float(cleaned)) if cleaned else None
    except (ValueError, TypeError):
        return None


def _safe_float(val):
    """Convert a value to float rounded to 1dp, returning None on failure."""
    if val is None or val == "":
        return None
    try:
        cleaned = str(val).replace(",", "").replace("~", "").strip()
        cleaned = re.sub(r'[^\d.\-]', '', cleaned)
        return round(float(cleaned), 1) if cleaned else None
    except (ValueError, TypeError):
        return None


def _fallback_data():
    """Hardcoded seed data from Hungry Jack's Australia menu (March 2026).
    Energy values converted from kJ to kcal, sodium from mg to salt g."""
    today = str(date.today())
    raw = [
        # (category, name, kcal, protein, carbs, fat, salt_g, description)
        ("Whopper & Beef", "Whopper\u00ae", 582, 28.1, 46.6, 45.2, 2.1, ""),
        ("Whopper & Beef", "Whopper\u00ae Cheese", 657, 32.7, 47.5, 51.0, 2.9, ""),
        ("Whopper & Beef", "Whopper\u00ae Junior", 294, 13.5, 28.6, 20.7, 1.1, ""),
        ("Whopper & Beef", "Double Whopper\u00ae", 847, 47.4, 46.6, 66.3, 2.3, ""),
        ("Whopper & Beef", "Cheeseburger", 322, 15.8, 28.3, 16.0, 1.5, ""),
        ("Whopper & Beef", "Hamburger", 285, 13.5, 27.9, 13.1, 1.2, ""),
        ("Whopper & Beef", "Bacon Deluxe", 512, 29.7, 27.1, 38.7, 2.1, ""),
        ("Chicken Burgers", "Chicken Royale", 336, 11.5, 41.7, 27.2, 1.6, ""),
        ("Chicken Burgers", "Grilled Chicken", 350, 22.4, 26.7, 17.0, 1.7, ""),
        ("Chicken Burgers", "Classic Jack's Fried Chicken", 679, 36.1, 55.2, 48.3, 3.0, ""),
        ("Sides & Snacks", "Thick Cut Chips", 308, 3.8, 41.1, 14.3, 1.5, ""),
        ("Sides & Snacks", "Battered Onion Rings", 286, 2.6, 23.6, 20.4, 0.8, ""),
        ("Sides & Snacks", "18 Nuggets & Sauces", 767, 42.0, 61.2, 39.6, 3.1, ""),
        ("Veggie", "Plant Based Whopper\u00ae", 554, 24.6, 49.8, 40.7, 2.9, ""),
        ("Veggie", "Veggie Whopper\u00ae Cheese", 544, 17.6, 61.9, 37.5, 2.9, ""),
        ("Breakfast", "BBQ Brekky Wrap", 628, 30.1, 47.2, 35.9, 2.9, ""),
        ("Breakfast", "Hash Brown", 164, 1.4, 15.2, 11.0, 0.6, ""),
        ("Desserts", "Soft Serve Cone", 189, 5.5, 24.7, 7.6, 0.3, ""),
        ("Desserts", "Chocolate Sundae", 532, 14.2, 73.9, 19.7, 0.9, ""),
        ("Desserts", "Storm OREO\u00ae", 569, 15.0, 77.3, 21.9, 1.1, ""),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, salt, desc in raw:
        items.append({
            "restaurant": "Hungry Jacks",
            "category": cat,
            "item": name,
            "description": desc,
            "calories_kcal": kcal,
            "protein_g": prot,
            "carbs_g": carbs,
            "fat_g": fat,
            "fibre_g": None,
            "salt_g": salt,
            "allergens": [],
            "dietary_flags": infer_dietary_flags(name, desc),
            "source_url": SOURCE_URL,
            "scraped_at": today,
        })
    print(f"  [HungryJacks] Using {len(items)} fallback items")
    return items
