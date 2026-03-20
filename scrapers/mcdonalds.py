"""
McDonald's UK nutrition scraper
McDonald's exposes menu data via an internal API used by their website.
Also scrapes their vegan/vegetarian category pages for source dietary flags.
"""

import requests
import json
import re
from datetime import date

from scrapers.dietary_utils import infer_dietary_flags

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HobbyNutritionBot/1.0; personal use)",
    "Accept": "application/json, text/html",
    "Referer": "https://www.mcdonalds.com/gb/en-gb/",
}

# McDonald's internal menu API (UK)
MENU_API = (
    "https://www.mcdonalds.com/gb/en-gb/eat/nutritioninfo.html"
)

# Their nutrition data API endpoint
NUTRITION_API = "https://www.mcdonalds.com/dnaapp/itemDetails"


def scrape():
    print("  [McDonalds] Fetching nutrition data...")

    # Fetch source dietary flags from McDonalds vegan/vegetarian pages
    dietary_map = _fetch_dietary_categories()

    items = []

    # Try the nutrition JSON endpoint McDonald's uses for their interactive tool
    try:
        resp = requests.get(
            "https://www.mcdonalds.com/content/dam/sites/gb/nfl/feeding-business/"
            "nutrition-data/GB_NutritionData_en_GB.json",
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            items = _parse_mcdonalds_json(data, dietary_map)
            if items:
                print(f"  [McDonalds] Scraped {len(items)} items via JSON endpoint")
                return items
    except Exception as e:
        print(f"  [McDonalds] JSON endpoint failed: {e}")

    # Fallback to hardcoded seed data
    print("  [McDonalds] Using fallback data")
    return _fallback_data(dietary_map)


def _fetch_dietary_categories():
    """
    Fetch McDonald's vegan and vegetarian category pages to build a map
    of product URL slugs to dietary flags.
    Returns dict: {"vegan-mcplant": "vegan", "fries-medium": "vegetarian", ...}
    """
    dietary_map = {}  # slug -> "vegan" or "vegetarian"

    for diet, url in [
        ("vegan", "https://www.mcdonalds.com/gb/en-gb/menu/vegan.html"),
        ("vegetarian", "https://www.mcdonalds.com/gb/en-gb/menu/vegetarian.html"),
    ]:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            # Extract product slugs from href links
            for m in re.finditer(
                r'href="/gb/en-gb/product/([^"]+?)\.html"', resp.text
            ):
                slug = m.group(1)
                # Vegan takes priority over vegetarian
                if slug not in dietary_map:
                    dietary_map[slug] = diet
        except Exception:
            continue

    if dietary_map:
        vegan_count = sum(1 for v in dietary_map.values() if v == "vegan")
        veg_count = sum(1 for v in dietary_map.values() if v == "vegetarian")
        print(f"  [McDonalds] Source dietary data: {vegan_count} vegan, {veg_count} vegetarian")

    return dietary_map


def _match_dietary(item_name, dietary_map):
    """Match an item name to dietary flags from the source map."""
    if not dietary_map:
        return infer_dietary_flags(item_name)

    # Normalise the item name to a slug-like form for matching
    slug = item_name.lower().replace("'", "").replace("&", "and")
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')

    for map_slug, diet in dietary_map.items():
        # Check if the map slug contains the item slug or vice versa
        map_normalised = map_slug.lower().replace("-", " ")
        item_normalised = item_name.lower()
        if (map_normalised in item_normalised or
                item_normalised in map_normalised or
                slug == map_slug):
            return [diet]

    return infer_dietary_flags(item_name)


def _parse_mcdonalds_json(data, dietary_map=None):
    items = []
    today = str(date.today())

    if isinstance(data, list):
        products = data
    elif isinstance(data, dict):
        products = data.get("items") or data.get("products") or data.get("menu") or []
    else:
        return []

    for p in products:
        name = p.get("name") or p.get("item") or p.get("title") or "Unknown"
        cal = _find_nutrient(p, ["calories", "energy", "kcal", "cal"])
        items.append({
            "restaurant": "McDonalds",
            "category": p.get("category") or p.get("menuCategory") or "Menu",
            "item": name,
            "description": p.get("description") or "",
            "calories_kcal": _safe_int(cal),
            "protein_g": _safe_float(_find_nutrient(p, ["protein"])),
            "carbs_g": _safe_float(_find_nutrient(p, ["carbohydrate", "carbs", "totalCarbohydrate"])),
            "fat_g": _safe_float(_find_nutrient(p, ["fat", "totalFat"])),
            "fibre_g": _safe_float(_find_nutrient(p, ["fibre", "fiber", "dietaryFiber"])),
            "salt_g": _safe_float(_find_nutrient(p, ["salt", "sodium"])),
            "allergens": p.get("allergens") or [],
            "dietary_flags": _match_dietary(name, dietary_map),
            "location": "National",
            "source_url": "https://www.mcdonalds.com/gb/en-gb/menu/vegan.html",
            "scraped_at": today,
        })
    return items


def _find_nutrient(product, keys):
    """Search for a nutrient value across multiple possible key names."""
    nutrition = product.get("nutrition") or product.get("nutrients") or product
    for key in keys:
        val = nutrition.get(key)
        if val is not None:
            if isinstance(val, dict):
                return val.get("value") or val.get("amount") or val.get("per100g")
            return val
    return None


def _safe_int(val):
    try:
        return int(float(val)) if val is not None else None
    except (ValueError, TypeError):
        return None


def _safe_float(val):
    try:
        return round(float(val), 1) if val is not None else None
    except (ValueError, TypeError):
        return None


def _fallback_data(dietary_map=None):
    """
    Hardcoded seed data for McDonald's UK.
    Source: mcdonalds.com/gb/en-gb (verified March 2026)
    """
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, fibre, salt
        ("Burgers", "Big Mac", 508, 27, 41, 25, 3, 2.2),
        ("Burgers", "Quarter Pounder with Cheese", 518, 32, 36, 26, 2, 2.4),
        ("Burgers", "McChicken Sandwich", 388, 21, 41, 15, 2, 1.8),
        ("Burgers", "Filet-O-Fish", 329, 16, 35, 13, 2, 1.5),
        ("Burgers", "Cheeseburger", 299, 16, 30, 12, 1, 1.7),
        ("Burgers", "Double Cheeseburger", 440, 26, 30, 22, 1, 2.3),
        ("Burgers", "Hamburger", 253, 14, 29, 8, 1, 1.2),
        ("Burgers", "McPlant", 426, 22, 39, 18, 5, 2.1),
        ("Chicken & Fish", "Chicken McNuggets x6", 259, 16, 19, 13, 1, 1.0),
        ("Chicken & Fish", "Chicken McNuggets x9", 388, 24, 28, 19, 1, 1.5),
        ("Chicken & Fish", "Chicken Selects x3", 330, 22, 28, 14, 1, 1.2),
        ("Chicken & Fish", "Crispy McBacon Burger", 491, 26, 45, 22, 2, 2.5),
        ("Sides", "Medium Fries", 337, 4, 44, 16, 4, 0.5),
        ("Sides", "Large Fries", 444, 5, 57, 21, 5, 0.7),
        ("Sides", "Small Fries", 230, 3, 30, 11, 3, 0.3),
        ("Sides", "Side Salad", 15, 1, 2, 0, 1, 0.1),
        ("Sides", "Corn Cups", 90, 3, 15, 2, 2, 0.2),
        ("Sides", "Mozzarella Dippers x3", 175, 8, 17, 8, 1, 0.9),
        ("Breakfast", "Egg McMuffin", 291, 17, 27, 11, 1, 2.0),
        ("Breakfast", "Sausage McMuffin", 399, 18, 27, 22, 1, 2.3),
        ("Breakfast", "Big Breakfast with Pancakes", 738, 31, 71, 36, 3, 3.8),
        ("Breakfast", "Hash Brown", 150, 1, 16, 9, 1, 0.5),
        ("Breakfast", "Pancakes & Syrup", 424, 10, 81, 9, 2, 1.2),
        ("Desserts & Drinks", "McFlurry Oreo", 310, 8, 49, 8, 0, 0.4),
        ("Desserts & Drinks", "Milkshake Medium Chocolate", 426, 12, 69, 10, 0, 0.6),
        ("Desserts & Drinks", "Apple Pie", 253, 3, 34, 12, 2, 0.4),
        ("Desserts & Drinks", "Caramel Sundae", 285, 6, 50, 7, 0, 0.4),
        ("Salads & Wraps", "Grilled Chicken Salad", 105, 18, 6, 2, 2, 0.8),
        ("Salads & Wraps", "Crispy Chicken & Bacon Salad", 230, 22, 8, 13, 2, 1.5),
        ("Salads & Wraps", "Veggie Wrap", 390, 13, 51, 14, 4, 1.4),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, fibre, salt in raw:
        items.append({
            "restaurant": "McDonalds",
            "category": cat,
            "item": name,
            "description": "",
            "calories_kcal": kcal,
            "protein_g": prot,
            "carbs_g": carbs,
            "fat_g": fat,
            "fibre_g": fibre,
            "salt_g": salt,
            "allergens": [],
            "dietary_flags": _match_dietary(name, dietary_map),
            "location": "National",
            "source_url": "https://www.mcdonalds.com/gb/en-gb/menu/vegan.html",
            "scraped_at": today,
        })
    print(f"  [McDonalds] Using {len(items)} fallback items")
    return items
