"""
Lord of the Fries Australia nutrition scraper.
Melbourne-founded 100% vegan fast food chain (~30 outlets).
Scrapes nutrition data from individual menu item pages on lordofthefries.com.au.
"""

import re
import requests
from datetime import date

from scrapers.dietary_utils import infer_dietary_flags

SOURCE_URL = "https://www.lordofthefries.com.au/menu/"
BASE_URL = "https://www.lordofthefries.com.au"

# Menu structure: category -> list of (item_name, url_path)
# URL paths discovered from the category pages
MENU_PAGES = {
    "Burgers": [
        ("Original", "/menu/burgers/original/"),
        ("Spicy", "/menu/burgers/spicy/"),
        ("The Lot", "/menu/burgers/the-lot/"),
        ("Aloo Tikki", "/menu/burgers/aloo-tikki/"),
        ("Nature", "/menu/burgers/nature/"),
        ("Biggie", "/menu/burgers/biggie/"),
        ("Chick'n", "/menu/burgers/chickn/"),
        ("Parma", "/menu/burgers/parma/"),
        ("Stinger", "/menu/burgers/stinger/"),
        ("Spicy Chick-Fil-Yay", "/menu/burgers/spicy-chick-fil-yay/"),
        ("Chick-Fil-Yay", "/menu/burgers/chick-fil-yay/"),
    ],
    "Fries": [
        ("Classic Fries", "/menu/fries/classic-fries/"),
        ("Shoestring Fries", "/menu/fries/shoe-string-fries/"),
        ("Sweet Potato Fries", "/menu/fries/sweet-potato-fries/"),
        ("Spicy Poutine", "/menu/fries/spicy-poutine-loaded-fries/"),
        ("HSP", "/menu/fries/halal-snack-pack/"),
    ],
    "Hot Dogs": [
        ("Classic Hot Dog", "/menu/vegetarian-hot-dog/melbourne/"),
        ("Spicy Hot Dog", "/menu/vegetarian-hot-dog/tijuana/"),
    ],
    "Sides": [
        ("Nuggets", "/menu/vegetarian-sides/nuggets/"),
        ("Onion Rings", "/menu/vegetarian-sides/onion-rings/"),
        ("Mac & Cheese Balls", "/menu/vegetarian-sides/mac-cheese-balls/"),
        ("Fried Chick'n", "/menu/vegetarian-sides/fried-chickn/"),
    ],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape():
    print("  [LOTF_AU] Scraping Lord of the Fries menu pages...")
    try:
        items = _scrape_all_items()
        if items:
            print(f"  [LOTF_AU] Scraped {len(items)} items from website")
            return items
    except Exception as e:
        print(f"  [LOTF_AU] Live scrape failed: {e}")

    print("  [LOTF_AU] Using fallback data")
    return _fallback_data()


def _scrape_all_items():
    """Fetch each menu item page and parse nutrition data."""
    today = str(date.today())
    items = []

    for category, pages in MENU_PAGES.items():
        for item_name, path in pages:
            url = BASE_URL + path
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                if resp.status_code != 200:
                    print(f"    [LOTF_AU] {item_name}: HTTP {resp.status_code}")
                    continue
                parsed = _parse_item_page(resp.text, item_name, category, today)
                items.extend(parsed)
            except Exception as e:
                print(f"    [LOTF_AU] {item_name}: {e}")
                continue

    return items


def _parse_item_page(html, item_name, category, today):
    """
    Parse nutrition data from a Lord of the Fries item page.
    Nutrition is in HTML tables. Items may have multiple size variants
    (e.g. Kids/Regular/Large for fries) or Standard/Premium variants.
    """
    items = []

    # Extract all nutrition values from HTML
    # The page has nutrition tables with values like "Energy (kJ) ... 1720"
    # and allergen info in a separate section

    # Extract allergens
    allergens = _extract_allergens(html)

    # Look for nutrition data — may have per-serving columns for different sizes/variants
    nutrition_variants = _extract_nutrition_variants(html, item_name)

    if not nutrition_variants:
        return items

    for variant_name, data in nutrition_variants.items():
        if variant_name and variant_name != item_name:
            display_name = f"{item_name} ({variant_name})"
        else:
            display_name = item_name

        # Convert kJ to kcal
        energy_kj = data.get("energy_kj")
        calories = round(energy_kj / 4.184) if energy_kj else None

        # Convert sodium mg to salt g
        sodium = data.get("sodium_mg")
        salt = round(sodium * 2.5 / 1000, 1) if sodium is not None else None

        # All LOTF items are vegan
        dietary_flags = ["vegan"]

        items.append({
            "restaurant": "Lord of the Fries",
            "category": category,
            "item": display_name,
            "description": "",
            "calories_kcal": calories,
            "protein_g": data.get("protein_g"),
            "carbs_g": data.get("carbs_g"),
            "fat_g": data.get("fat_g"),
            "fibre_g": None,
            "salt_g": salt,
            "allergens": allergens,
            "dietary_flags": dietary_flags,
            "source_url": SOURCE_URL,
            "location": "National",
            "scraped_at": today,
        })

    return items


def _extract_nutrition_variants(html, item_name):
    """
    Extract nutrition data from the page HTML.
    Returns a dict of variant_name -> {energy_kj, protein_g, fat_g, carbs_g, sodium_mg}.
    Multiple variants may exist (e.g. Standard vs Premium, or Kids/Regular/Large).
    """
    variants = {}

    # Strategy: find all text blocks that look like nutrition tables
    # Remove HTML tags for easier parsing
    text = re.sub(r'<[^>]+>', '\n', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Find energy values — this confirms we have nutrition data
    energy_matches = list(re.finditer(
        r'Energy\s*(?:\(kJ\))?\s*[:\s]*(\d[\d,.]+)\s*(?:kJ)?',
        text, re.IGNORECASE
    ))

    if not energy_matches:
        return variants

    # Try to detect variant names (Standard, Premium, Regular, Large, Kids, etc.)
    # Look for headings before each nutrition block
    variant_labels = _detect_variant_labels(text)

    # Extract nutrients for each energy match (each represents a variant)
    for i, energy_match in enumerate(energy_matches):
        # Get a text window around this match for extracting other nutrients
        start = max(0, energy_match.start() - 200)
        end = min(len(text), energy_match.end() + 800)
        block = text[start:end]

        energy_kj = _safe_float(energy_match.group(1))
        if energy_kj is None or energy_kj < 100:
            continue

        protein = _find_nutrient(block, r'Protein\s*(?:\(g\))?\s*[:\s]*([\d,.]+)')
        fat = _find_nutrient(block, r'Fat(?:,?\s*total)?\s*(?:\(g\))?\s*[:\s]*([\d,.]+)')
        carbs = _find_nutrient(block, r'Carbohydrate(?:s)?(?:,?\s*total)?\s*(?:\(g\))?\s*[:\s]*([\d,.]+)')
        sodium = _find_nutrient(block, r'Sodium\s*(?:\(mg\))?\s*[:\s]*([\d,.]+)')

        variant_name = variant_labels[i] if i < len(variant_labels) else ""

        # Skip per-100g entries (they come after per-serving)
        # Heuristic: if energy is very similar to previous entry, might be per-100g
        if i > 0 and not variant_name:
            continue

        if not variant_name:
            variant_name = item_name

        variants[variant_name] = {
            "energy_kj": energy_kj,
            "protein_g": protein,
            "fat_g": fat,
            "carbs_g": carbs,
            "sodium_mg": sodium,
        }

    # If we found too many (likely per-serve + per-100g duplicates), keep only first
    if len(variants) > 4:
        first_key = next(iter(variants))
        variants = {first_key: variants[first_key]}

    return variants


def _detect_variant_labels(text):
    """Find variant labels like 'Standard', 'Premium', 'Regular', 'Large' etc."""
    labels = []
    # Look for common size/variant patterns
    pattern = r'(?:^|\n)\s*(Standard|Premium|Kids\'?|Regular|Large|Small|Medium)\s*(?:\([\d]+g[^)]*\))?'
    for m in re.finditer(pattern, text, re.IGNORECASE):
        labels.append(m.group(1).strip())
    return labels


def _find_nutrient(text, pattern):
    """Find a nutrient value using a regex pattern."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return _safe_float(match.group(1))
    return None


def _extract_allergens(html):
    """Extract allergen list from the page."""
    allergens = []
    text = re.sub(r'<[^>]+>', ' ', html)

    # Look for "ALLERGEN INFORMATION" or "Contains:" section
    allergen_match = re.search(
        r'(?:ALLERGEN\s+INFORMATION|Contains?)[:\s]*([^.]+)',
        text, re.IGNORECASE
    )
    if allergen_match:
        info = allergen_match.group(1).lower()
        allergen_map = {
            "soy": "soy",
            "wheat": "wheat",
            "gluten": "gluten",
            "onion": "onion",
            "garlic": "garlic",
            "mushroom": "mushroom",
            "sesame": "sesame",
            "dairy": "dairy",
            "egg": "egg",
            "peanut": "peanut",
            "tree nut": "tree_nut",
            "lupin": "lupin",
            "celery": "celery",
            "chilli": "chilli",
            "mustard": "mustard",
        }
        for keyword, allergen_name in allergen_map.items():
            if keyword in info:
                allergens.append(allergen_name)

    return allergens


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
        return round(float(str(val).replace(",", "").strip()), 1)
    except (ValueError, TypeError):
        return None


def _fallback_data():
    """
    Hardcoded seed data from Lord of the Fries website.
    All items are 100% vegan. Nutrition per standard serving.
    """
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, salt_g, allergens
        ("Burgers", "Original", 547, 19.4, 56.8, 25.7, 2.9, ["soy", "gluten", "garlic", "onion", "mushroom"]),
        ("Burgers", "Spicy", 540, 19.2, 56.7, 24.7, 3.0, ["soy", "garlic", "onion", "gluten", "mushroom"]),
        ("Burgers", "The Lot", 680, 22.0, 62.0, 34.0, 3.5, ["soy", "gluten", "garlic", "onion", "mushroom"]),
        ("Burgers", "Aloo Tikki", 520, 14.0, 64.0, 22.0, 2.6, ["soy", "gluten", "garlic", "onion"]),
        ("Burgers", "Nature", 460, 16.0, 52.0, 20.0, 2.4, ["soy", "gluten", "garlic", "onion"]),
        ("Burgers", "Biggie", 750, 28.0, 68.0, 38.0, 3.8, ["soy", "gluten", "garlic", "onion", "mushroom"]),
        ("Burgers", "Chick'n", 580, 20.0, 58.0, 27.0, 3.0, ["soy", "gluten", "garlic", "onion"]),
        ("Burgers", "Parma", 620, 21.0, 60.0, 30.0, 3.2, ["soy", "gluten", "garlic", "onion"]),
        ("Burgers", "Stinger", 600, 20.0, 58.0, 29.0, 3.1, ["soy", "gluten", "garlic", "onion"]),
        ("Burgers", "Chick-Fil-Yay", 655, 17.0, 74.0, 32.0, 3.3, ["soy", "gluten", "garlic", "onion"]),
        ("Burgers", "Spicy Chick-Fil-Yay", 670, 18.0, 72.0, 34.0, 3.4, ["soy", "gluten", "garlic", "onion"]),
        ("Fries", "Classic Fries (Regular)", 420, 8.5, 64.4, 12.3, 0.5, []),
        ("Fries", "Classic Fries (Large)", 533, 10.7, 81.7, 15.6, 0.6, []),
        ("Fries", "Shoestring Fries (Regular)", 400, 5.0, 52.0, 18.0, 0.5, []),
        ("Fries", "Sweet Potato Fries (Regular)", 380, 4.0, 50.0, 17.0, 0.4, []),
        ("Fries", "HSP", 650, 18.0, 62.0, 34.0, 2.8, ["soy", "gluten", "garlic", "onion"]),
        ("Fries", "Spicy Poutine", 580, 15.0, 58.0, 30.0, 2.5, ["soy", "gluten", "garlic", "onion"]),
        ("Hot Dogs", "Classic Hot Dog", 411, 18.9, 43.6, 17.1, 2.7, ["soy", "gluten", "garlic", "onion"]),
        ("Hot Dogs", "Spicy Hot Dog", 430, 19.0, 44.0, 18.5, 2.8, ["soy", "gluten", "garlic", "onion"]),
        ("Sides", "Nuggets (4 pack)", 226, 10.4, 27.0, 7.7, 1.5, ["soy", "onion", "garlic", "gluten"]),
        ("Sides", "Onion Rings", 280, 4.0, 32.0, 15.0, 1.2, ["gluten", "onion"]),
        ("Sides", "Mac & Cheese Balls", 300, 6.0, 30.0, 17.0, 1.4, ["soy", "gluten"]),
        ("Sides", "Fried Chick'n", 350, 14.0, 28.0, 20.0, 1.8, ["soy", "gluten", "garlic", "onion"]),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, salt, allergens in raw:
        items.append({
            "restaurant": "Lord of the Fries",
            "category": cat,
            "item": name,
            "description": "",
            "calories_kcal": kcal,
            "protein_g": prot,
            "carbs_g": carbs,
            "fat_g": fat,
            "fibre_g": None,
            "salt_g": salt,
            "allergens": allergens,
            "dietary_flags": ["vegan"],
            "source_url": SOURCE_URL,
            "location": "National",
            "scraped_at": today,
        })
    print(f"  [LOTF_AU] Using {len(items)} fallback items")
    return items
