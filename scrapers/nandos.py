"""
Nandos UK nutrition scraper
Fetches structured menu data from Nandos' Gatsby page-data JSON endpoint.
Includes full dietary flags (vegan, vegetarian, gluten-free) and allergens
directly from the source data.
"""

import requests
import json
import re
from datetime import date

from scrapers.dietary_utils import infer_dietary_flags

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HobbyNutritionBot/1.0; personal use)",
    "Accept": "application/json",
}

# Gatsby page-data endpoint — returns full menu JSON without JS rendering
PAGE_DATA_URL = "https://www.nandos.co.uk/food/menu/page-data/index/page-data.json"


def scrape():
    print("  [Nandos] Fetching menu data...")
    try:
        resp = requests.get(PAGE_DATA_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [Nandos] Request failed: {e}")
        return _fallback_data()

    items = _parse_page_data(data)
    if items:
        print(f"  [Nandos] Scraped {len(items)} items")
        return items

    print("  [Nandos] Could not parse page data, using fallback")
    return _fallback_data()


def _parse_page_data(data):
    """Parse the Gatsby page-data JSON for menu items."""
    try:
        sections = data["result"]["data"]["nandos"]["menu"]["sections"]
    except (KeyError, TypeError):
        return []

    today = str(date.today())
    items = []

    for section in sections:
        category = section.get("displayName", "Menu")
        for product in section.get("items", []):
            name = product.get("displayName", "")
            if not name:
                continue

            description = product.get("description", "") or ""

            # Dietary flags directly from source
            diets = product.get("diets", [])
            dietary_flags = []
            if "VEGAN" in diets:
                dietary_flags.append("vegan")
            if "VEGETARIAN" in diets and "vegan" not in dietary_flags:
                dietary_flags.append("vegetarian")
            if "GLUTEN_FREE" in diets:
                dietary_flags.append("gluten_free")

            # Allergens from source — only include confirmed ("YES")
            allergens = []
            for a in product.get("allergens", []):
                if a.get("present") == "YES":
                    allergen_name = a.get("name", "")
                    # Normalise: GLUTEN_WHEAT -> gluten (wheat), etc.
                    clean = allergen_name.lower().replace("_", " ")
                    allergens.append(clean)

            # Nutrition — values are in milligrams, convert to grams
            nutrition = {}
            portions = (product.get("nutritionalInfo") or {}).get("factsForPortionSizes", [])
            if portions:
                p = portions[0]
                nutrition = {
                    "kcal": p.get("energyKcal"),
                    "protein": _mg_to_g(p.get("proteinMg")),
                    "carbs": _mg_to_g(p.get("totalCarbsMg")),
                    "fat": _mg_to_g(p.get("fatMg")),
                    "fibre": _mg_to_g(p.get("fibreMg")),
                    "salt": _mg_to_g(p.get("saltMg")),
                }

            items.append({
                "restaurant": "Nandos",
                "category": category,
                "item": name,
                "description": description,
                "calories_kcal": _safe_int(nutrition.get("kcal")),
                "protein_g": nutrition.get("protein"),
                "carbs_g": nutrition.get("carbs"),
                "fat_g": nutrition.get("fat"),
                "fibre_g": nutrition.get("fibre"),
                "salt_g": nutrition.get("salt"),
                "allergens": allergens,
                "dietary_flags": dietary_flags if dietary_flags else infer_dietary_flags(name, description),
                "location": "National",
                "source_url": "https://www.nandos.co.uk/food/menu",
                "scraped_at": today,
            })

    return items


def _mg_to_g(mg_val):
    """Convert milligrams to grams, rounded to 1 decimal."""
    if mg_val is None:
        return None
    try:
        return round(float(mg_val) / 1000, 1)
    except (ValueError, TypeError):
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
    Hardcoded seed data for Nandos — used when live scrape fails.
    Source: nandos.co.uk/food/menu (verified March 2026)
    """
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, fibre, salt
        ("Chicken", "¼ Chicken Breast", 289, 52, 0, 9, 0, 0.6),
        ("Chicken", "¼ Chicken Leg & Thigh", 373, 34, 0, 26, 0, 0.8),
        ("Chicken", "½ Chicken", 596, 84, 1, 30, 0, 1.3),
        ("Chicken", "Whole Chicken", 1157, 165, 2, 57, 0, 2.4),
        ("Chicken", "Butterfly Chicken Breast", 331, 60, 1, 10, 0, 0.7),
        ("Chicken", "3 Chicken Thighs", 418, 44, 1, 27, 0, 1.1),
        ("Chicken", "10 PERi-PERi Wings", 782, 95, 2, 43, 0, 2.1),
        ("Burgers, Pittas & Wraps", "Classic Chicken Burger", 530, 44, 46, 18, 2, 2.1),
        ("Burgers, Pittas & Wraps", "Great Imitator Wrap", 558, 23, 58, 24, 5, 2.4),
        ("Burgers, Pittas & Wraps", "Chicken Pitta", 428, 41, 43, 10, 3, 1.8),
        ("Burgers, Pittas & Wraps", "Chicken Caesar Wrap", 619, 40, 51, 27, 3, 2.6),
        ("Burgers, Pittas & Wraps", "Spiced Chickpea Burger", 535, 22, 64, 19, 7, 2.3),
        ("Sides", "PERi-Salted Chips", 450, 6, 60, 21, 5, 1.2),
        ("Sides", "Fully Loaded Chips", 1102, 28, 78, 74, 7, 3.1),
        ("Sides", "Spicy Rice", 246, 5, 49, 3, 2, 0.8),
        ("Sides", "Coleslaw", 190, 1, 10, 16, 2, 0.5),
        ("Sides", "Rainbow Slaw", 132, 2, 14, 8, 3, 0.4),
        ("Sides", "Tenderstem Broccoli", 32, 3, 3, 1, 3, 0.2),
        ("Sides", "Corn on the Cob", 168, 4, 30, 4, 4, 0.1),
        ("Sides", "PERi-Mac & Cheese", 494, 16, 45, 27, 2, 1.8),
        ("Sides", "Garlic Bread", 307, 9, 43, 11, 2, 1.1),
        ("Sides", "Halloumi Sticks", 379, 19, 14, 28, 1, 2.4),
        ("Starters", "Houmous with PERi Drizzle", 398, 13, 32, 25, 8, 1.3),
        ("Starters", "Spicy Mixed Olives", 138, 1, 2, 14, 2, 2.1),
        ("Salads & Bowls", "Garden Salad", 17, 1, 2, 0, 2, 0.1),
        ("Salads & Bowls", "Mediterranean Salad", 350, 10, 28, 22, 6, 0.8),
        ("Salads & Bowls", "Caesar Salad", 412, 35, 22, 20, 3, 1.6),
        ("Desserts", "Chocolate Mousse", 384, 5, 38, 23, 1, 0.2),
        ("Desserts", "Mango Gelado", 93, 1, 22, 0, 0, 0.1),
        ("Desserts", "Choc-A-Lot Cake", 425, 5, 52, 22, 2, 0.5),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, fibre, salt in raw:
        items.append({
            "restaurant": "Nandos",
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
            "source_url": "https://www.nandos.co.uk/food/menu",
            "scraped_at": today,
        })
    print(f"  [Nandos] Using {len(items)} fallback items")
    return items
