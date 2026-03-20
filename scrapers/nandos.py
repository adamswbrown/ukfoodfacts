"""
Nandos UK nutrition scraper
Fetches from https://www.nandos.co.uk/food/menu
Nandos renders menu data as JSON in a <script> tag (Next.js __NEXT_DATA__)
"""

import requests
import json
import re
from datetime import date

from scrapers.dietary_utils import infer_dietary_flags

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HobbyNutritionBot/1.0; personal use)",
    "Accept": "text/html,application/xhtml+xml",
}


def scrape():
    print("  [Nandos] Fetching menu page...")
    try:
        resp = requests.get(
            "https://www.nandos.co.uk/food/menu", headers=HEADERS, timeout=15
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"  [Nandos] Request failed: {e}")
        return []

    # Nandos (Next.js) embeds all menu data in __NEXT_DATA__ JSON script tag
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        resp.text,
        re.DOTALL,
    )
    if not match:
        print("  [Nandos] Could not find __NEXT_DATA__ - site structure may have changed")
        return _fallback_data()

    try:
        next_data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"  [Nandos] JSON parse error: {e}")
        return _fallback_data()

    items = []
    today = str(date.today())

    # Walk the page props to find menu sections
    try:
        # Path varies by Next.js version; try common paths
        page_props = next_data.get("props", {}).get("pageProps", {})
        menu_data = (
            page_props.get("menu")
            or page_props.get("menuData")
            or page_props.get("categories")
        )

        if not menu_data:
            print("  [Nandos] Menu structure not found in expected location")
            return _fallback_data()

        for category in menu_data:
            cat_name = category.get("name", "Unknown")
            products = category.get("products") or category.get("items") or []
            for product in products:
                nutrition = product.get("nutrition") or product.get("nutritionInfo") or {}
                items.append({
                    "restaurant": "Nandos",
                    "category": cat_name,
                    "item": product.get("name", "Unknown"),
                    "description": product.get("description", ""),
                    "calories_kcal": _safe_int(nutrition.get("calories") or nutrition.get("energy")),
                    "protein_g": _safe_float(nutrition.get("protein")),
                    "carbs_g": _safe_float(nutrition.get("carbohydrates") or nutrition.get("carbs")),
                    "fat_g": _safe_float(nutrition.get("fat") or nutrition.get("totalFat")),
                    "fibre_g": _safe_float(nutrition.get("fibre") or nutrition.get("fiber")),
                    "salt_g": _safe_float(nutrition.get("salt") or nutrition.get("sodium")),
                    "allergens": product.get("allergens", []),
                    "dietary_flags": infer_dietary_flags(
                        product.get("name", ""),
                        product.get("description", ""),
                        source_tags=product.get("tags") or product.get("dietaryInfo"),
                    ),
                    "location": "National",
                    "source_url": "https://www.nandos.co.uk/food/menu",
                    "scraped_at": today,
                })
    except Exception as e:
        print(f"  [Nandos] Parse error: {e}")
        return _fallback_data()

    if not items:
        print("  [Nandos] No items parsed, using fallback data")
        return _fallback_data()

    print(f"  [Nandos] Scraped {len(items)} items")
    return items


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
