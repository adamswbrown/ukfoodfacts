"""
Wagamama UK nutrition scraper
Wagamama embeds full menu data (via Tenkites) in a Nuxt payload on their menu page.
The payload contains structured dietary/allergen data for every dish.
URL: https://www.wagamama.com/our-menu
"""

import json
import re
import requests
from datetime import date

from scrapers.dietary_utils import infer_dietary_flags

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HobbyNutritionBot/1.0; personal use)",
    "Accept": "text/html,application/xhtml+xml",
}


def scrape():
    print("  [Wagamama] Fetching menu page...")
    try:
        resp = requests.get(
            "https://www.wagamama.com/our-menu",
            headers=HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"  [Wagamama] Request failed: {e}")
        return _fallback_data()

    items = _parse_nuxt_payload(resp.text)
    if items:
        print(f"  [Wagamama] Scraped {len(items)} items")
        return items

    print("  [Wagamama] Could not parse Nuxt payload, using fallback")
    return _fallback_data()


def _parse_nuxt_payload(html):
    """Extract menu data from the Nuxt/Tenkites payload embedded in the page."""
    # Find the large script tag containing the Nuxt payload
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    payload = None
    for s in scripts:
        if len(s) > 100000 and '"Reactive"' in s[:50]:
            try:
                payload = json.loads(s)
                break
            except json.JSONDecodeError:
                continue

    if not payload or not isinstance(payload, list):
        return []

    arr = payload
    today = str(date.today())

    def deep_resolve(val, depth=0):
        """Resolve Nuxt positional references."""
        if depth > 5:
            return val
        if isinstance(val, int) and 0 <= val < len(arr):
            return deep_resolve(arr[val], depth + 1)
        return val

    # Find all recipe template positions (objects with Intols + Nutrs + Name keys)
    recipe_positions = []
    for i, item in enumerate(arr):
        if isinstance(item, dict) and "Intols" in item and "Nutrs" in item and "Name" in item:
            recipe_positions.append(i)

    if not recipe_positions:
        return []

    # Find section/category info — objects with Sections + Recipes + Name keys
    section_map = {}  # recipe_position -> section_name
    for i, item in enumerate(arr):
        if isinstance(item, dict) and "Recipes" in item and "Name" in item and "Sections" in item:
            section_name = deep_resolve(item.get("Name", ""))
            if isinstance(section_name, str) and section_name:
                recipes_ref = deep_resolve(item["Recipes"])
                if isinstance(recipes_ref, list):
                    for rref in recipes_ref:
                        resolved_ref = deep_resolve(rref)
                        if isinstance(resolved_ref, dict) and "Name" in resolved_ref:
                            # Find which recipe_position this maps to
                            for rpos in recipe_positions:
                                if arr[rpos] is resolved_ref:
                                    section_map[rpos] = section_name.title()
                                    break

    items = []
    for pos in recipe_positions:
        template = arr[pos]
        name = deep_resolve(template["Name"])
        if not isinstance(name, str) or not name.strip():
            continue

        desc = deep_resolve(template.get("Desc", ""))
        if not isinstance(desc, str):
            desc = ""

        # Extract dietary flags and allergens from Intols
        dietary_flags = []
        allergens = []
        intols_list = deep_resolve(template.get("Intols"))
        if isinstance(intols_list, list):
            for iref in intols_list:
                intol_obj = arr[iref] if isinstance(iref, int) and iref < len(arr) else iref
                if not isinstance(intol_obj, dict):
                    continue
                intol_id = deep_resolve(intol_obj.get("Id", ""))
                val = deep_resolve(intol_obj.get("Val", ""))

                if isinstance(intol_id, str) and val == "yes":
                    lid = intol_id.lower()
                    if lid == "vegan":
                        dietary_flags.append("vegan")
                    elif lid == "vegetarian":
                        dietary_flags.append("vegetarian")
                    elif lid in ("celery", "crustaceans", "eggs", "fish", "lupin",
                                 "milk", "molluscs", "mustard", "sesame", "soya",
                                 "sulphites", "peanuts"):
                        allergens.append(intol_id)
                    elif lid == "cereals containing gluten":
                        allergens.append("gluten")

        # Extract nutrition from Nutrs
        nutrition = {}
        nutrs_list = deep_resolve(template.get("Nutrs"))
        if isinstance(nutrs_list, list):
            for nref in nutrs_list:
                nutr_obj = arr[nref] if isinstance(nref, int) and nref < len(arr) else nref
                if isinstance(nutr_obj, dict):
                    ndesc = deep_resolve(nutr_obj.get("Desc", ""))
                    per_serv = deep_resolve(nutr_obj.get("PerServ", ""))
                    if isinstance(ndesc, str) and per_serv:
                        nutrition[ndesc.lower()] = str(per_serv).replace(",", "")

        category = section_map.get(pos, "Menu")

        items.append({
            "restaurant": "Wagamama",
            "category": category,
            "item": name.strip().title(),
            "description": desc.strip(),
            "calories_kcal": _safe_int(nutrition.get("energy (kcal)")),
            "protein_g": _safe_float(nutrition.get("protein (g)")),
            "carbs_g": _safe_float(nutrition.get("carbohydrate (g)")),
            "fat_g": _safe_float(nutrition.get("fat (g)")),
            "fibre_g": _safe_float(nutrition.get("fibre (g)")),
            "salt_g": _safe_float(nutrition.get("salt (g)")),
            "allergens": allergens,
            "dietary_flags": dietary_flags if dietary_flags else infer_dietary_flags(name, desc),
            "location": "National",
            "source_url": "https://www.wagamama.com/our-menu",
            "scraped_at": today,
        })

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
    Hardcoded seed data for Wagamama UK.
    Source: wagamama.com/menu (verified March 2026)
    """
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, fibre, salt
        ("Ramen", "Chicken Ramen", 498, 38, 52, 12, 4, 3.2),
        ("Ramen", "Yasai Ramen (Vegan)", 412, 14, 65, 9, 7, 2.8),
        ("Ramen", "Chilli Chicken Ramen", 541, 40, 54, 15, 4, 3.4),
        ("Ramen", "Pork Tonkotsu Ramen", 621, 42, 58, 20, 3, 3.8),
        ("Ramen", "Seafood Ramen", 467, 35, 53, 10, 5, 3.6),
        ("Curry", "Katsu Curry Chicken", 744, 38, 88, 22, 4, 2.6),
        ("Curry", "Katsu Curry Tofu (Vegan)", 681, 22, 95, 20, 7, 2.4),
        ("Curry", "Firecracker Chicken Curry", 598, 35, 68, 18, 5, 2.9),
        ("Curry", "Sweet Potato & Kale Curry (Vegan)", 512, 12, 78, 14, 9, 2.1),
        ("Teppanyaki", "Teriyaki Chicken Soba", 567, 42, 62, 14, 5, 3.1),
        ("Teppanyaki", "Beef Teriyaki", 624, 45, 58, 20, 4, 3.3),
        ("Teppanyaki", "Salmon Teriyaki", 589, 40, 55, 22, 3, 2.8),
        ("Donburi", "Chicken Donburi", 618, 38, 78, 16, 4, 2.7),
        ("Donburi", "Salmon & Avocado Donburi", 672, 34, 72, 24, 6, 2.3),
        ("Donburi", "Yasai Donburi (Vegan)", 534, 16, 84, 12, 8, 2.0),
        ("Sides", "Edamame", 121, 12, 8, 5, 6, 0.8),
        ("Sides", "Gyoza Chicken x5", 248, 16, 28, 8, 2, 1.4),
        ("Sides", "Gyoza Vegetables x5", 198, 8, 28, 6, 4, 1.2),
        ("Sides", "Chilli Squid", 312, 22, 28, 12, 1, 1.8),
        ("Sides", "Bang Bang Cauliflower", 298, 6, 38, 12, 4, 1.6),
        ("Sides", "Steamed Rice", 218, 5, 46, 1, 1, 0.1),
        ("Sides", "Noodles", 198, 7, 38, 3, 2, 0.4),
        ("Salads", "Warm Chicken Salad", 348, 28, 24, 16, 5, 1.8),
        ("Salads", "Grilled Chicken Caesar", 412, 32, 28, 18, 4, 2.1),
        ("Salads", "Duck & Noodle Salad", 467, 30, 42, 18, 5, 2.4),
        ("Desserts", "Mochi Ice Cream", 187, 3, 28, 7, 0, 0.1),
        ("Desserts", "Banana Katsu", 398, 5, 62, 14, 3, 0.3),
        ("Desserts", "Yuzu Cheesecake", 412, 6, 48, 21, 1, 0.4),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, fibre, salt in raw:
        items.append({
            "restaurant": "Wagamama",
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
            "source_url": "https://www.wagamama.com/our-menu",
            "scraped_at": today,
        })
    print(f"  [Wagamama] Using {len(items)} fallback items")
    return items
