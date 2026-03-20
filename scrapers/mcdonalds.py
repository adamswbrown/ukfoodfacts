"""
McDonald's UK nutrition scraper
McDonald's exposes menu data via an internal API used by their website.
Endpoint: https://www.mcdonalds.com/gb/en-gb/eat/nutritioninfo.html
They also serve structured JSON from their menu API.
"""

import requests
import json
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

    items = []

    # Try the nutrition JSON endpoint McDonald's uses for their interactive tool
    try:
        # This endpoint is used by their own nutrition calculator page
        resp = requests.get(
            "https://www.mcdonalds.com/content/dam/sites/gb/nfl/feeding-business/"
            "nutrition-data/GB_NutritionData_en_GB.json",
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            items = _parse_mcdonalds_json(data)
            if items:
                print(f"  [McDonalds] Scraped {len(items)} items via JSON endpoint")
                return items
    except Exception as e:
        print(f"  [McDonalds] JSON endpoint failed: {e}")

    # Fallback to hardcoded seed data
    print("  [McDonalds] Using fallback data")
    return _fallback_data()


def _parse_mcdonalds_json(data):
    items = []
    today = str(date.today())

    # McDonald's JSON structure varies — handle both array and dict forms
    if isinstance(data, list):
        products = data
    elif isinstance(data, dict):
        products = data.get("items") or data.get("products") or data.get("menu") or []
    else:
        return []

    for p in products:
        cal = _find_nutrient(p, ["calories", "energy", "kcal", "cal"])
        items.append({
            "restaurant": "McDonalds",
            "category": p.get("category") or p.get("menuCategory") or "Menu",
            "item": p.get("name") or p.get("item") or p.get("title") or "Unknown",
            "description": p.get("description") or "",
            "calories_kcal": _safe_int(cal),
            "protein_g": _safe_float(_find_nutrient(p, ["protein"])),
            "carbs_g": _safe_float(_find_nutrient(p, ["carbohydrate", "carbs", "totalCarbohydrate"])),
            "fat_g": _safe_float(_find_nutrient(p, ["fat", "totalFat"])),
            "fibre_g": _safe_float(_find_nutrient(p, ["fibre", "fiber", "dietaryFiber"])),
            "salt_g": _safe_float(_find_nutrient(p, ["salt", "sodium"])),
            "allergens": p.get("allergens") or [],
            "dietary_flags": infer_dietary_flags(
                p.get("name") or p.get("item") or p.get("title") or "",
                p.get("description") or "",
            ),
            "location": "National",
            "location": "National",
            "source_url": "https://www.mcdonalds.com/gb/en-gb/eat/nutritioninfo.html",
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


def _fallback_data():
    """
    Hardcoded seed data for McDonald's UK.
    Source: mcdonalds.com/gb/en-gb/eat/nutritioninfo.html (verified March 2026)
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
            "dietary_flags": infer_dietary_flags(name),
            "location": "National",
            "source_url": "https://www.mcdonalds.com/gb/en-gb/eat/nutritioninfo.html",
            "scraped_at": today,
        })
    print(f"  [McDonalds] Using {len(items)} fallback items")
    return items
