"""
BurgerFuel New Zealand nutrition scraper
Scrapes the official BurgerFuel NZ nutritional info and allergen PDFs
hosted on Webflow CDN.
"""

from datetime import date

from scrapers.pdf_utils import download_pdf, extract_tables, clean_table, safe_int, safe_float
from scrapers.dietary_utils import infer_dietary_flags

NUTRITION_PDF_URL = (
    "https://cdn.prod.website-files.com/67b6723ca131505ad034f59b/"
    "684bf64d171c0a11202aeacd_BurgerFuel%20Products%20Nutritional%20"
    "Information%20Burgers%20NZ%2008-23.pdf"
)
ALLERGEN_PDF_URL = (
    "https://cdn.prod.website-files.com/67bc26a1dc4339ea29ceb640/"
    "69adfce5fc19550676fb17fb_burgerfuel-allergen-dietary-suitability"
    "-chart-06-03-2026.pdf"
)
SOURCE_URL = "https://www.burgerfuel.com/nz/menu"

# Map base burger names to category.  Items not found here get "Menu".
CATEGORY_KEYWORDS = {
    "american muscle": "Burgers",
    "bacon bbq roadster": "Burgers",
    "bambina": "Burgers",
    "bastard": "Burgers",
    "bio fuel": "Burgers",
    "c n cheese": "Burgers",
    "diablo": "Burgers",
    "ford freakout": "Burgers",
    "hamburgini": "Burgers",
    "peanut piston": "Burgers",
    "bacon backfire": "Burgers",
    "burnout": "Burgers",
    "ring burner": "Burgers",
    "chick chevelle": "Chicken",
    "chook royale": "Chicken",
    "drift chick": "Chicken",
    "t-bird": "Chicken",
    "modifried thunderbird": "Chicken",
    "flame thrower": "Chicken",
    "v-twin vege": "Vegetarian",
    "v8 vegan": "Vegan",
    "vege pinto": "Vegan",
    "combustion tofu": "Vegan",
    "kids cheeseburger": "Kids",
    "kids": "Kids",
    "teeny choppers": "Kids",
    "mini motobites": "Kids",
    "spud fries": "Sides",
    "kumara fries": "Sides",
    "kūmara fries": "Sides",
    "motobites": "Sides",
    "chicken fenders": "Sides",
    "choppers": "Sides",
    "shake": "Drinks",
    "thickshake": "Drinks",
    "banana": "Drinks",
    "caramel": "Drinks",
    "chocolate": "Drinks",
    "lime": "Drinks",
    "strawberry": "Drinks",
    "espresso": "Drinks",
    "camaro": "Drinks",
    "coke": "Drinks",
    "sprite": "Drinks",
    "l&p": "Drinks",
    "schweppes": "Drinks",
    "fanta": "Drinks",
    "most organics": "Drinks",
    "keri": "Drinks",
    "kiwi blue": "Drinks",
    "ginger beer": "Drinks",
}


def _categorise(item_name):
    """Assign a category based on item name keywords."""
    name_lower = item_name.lower()
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in name_lower:
            return category
    return "Menu"


def scrape():
    print("  [BurgerFuelNZ] Fetching nutrition PDF...")
    try:
        items = _scrape_live()
        if items:
            print(f"  [BurgerFuelNZ] Scraped {len(items)} items from PDFs")
            return items
    except Exception as e:
        print(f"  [BurgerFuelNZ] PDF scrape failed: {e}")

    print("  [BurgerFuelNZ] Using fallback data")
    return _fallback_data()


def _scrape_live():
    """Download both PDFs and merge nutrition + allergen data."""
    today = str(date.today())

    # --- Allergen PDF ---
    allergen_map = {}
    dietary_map = {}
    try:
        print("  [BurgerFuelNZ] Fetching allergen PDF...")
        allergen_pdf = download_pdf(ALLERGEN_PDF_URL)
        allergen_map, dietary_map = _parse_allergen_pdf(allergen_pdf)
        allergen_pdf.close()
        print(f"  [BurgerFuelNZ] Parsed allergens for {len(allergen_map)} items")
    except Exception as e:
        print(f"  [BurgerFuelNZ] Allergen PDF failed: {e}")

    # --- Nutrition PDF ---
    nutrition_pdf = download_pdf(NUTRITION_PDF_URL)
    items = _parse_nutrition_pdf(nutrition_pdf, allergen_map, dietary_map, today)
    nutrition_pdf.close()

    return items


def _parse_nutrition_pdf(pdf, allergen_map, dietary_map, today):
    """
    Parse the BurgerFuel nutrition PDF.

    Each page has 2–3 tables. Each table represents one item+variant combo
    (e.g. "AMERICAN MUSCLE SINGLE SERVED ON A WHOLEMEAL BUN").

    Table structure (3 columns, 10 rows):
      Row 0: [item_name_and_variant, '', '']
      Row 1: ['AVERAGE SERVING SIZE: ...', 'AVERAGE PER 100G', 'AVERAGE PER SERVE (...)']
      Row 2: ['ENERGY (KJ)', per_100g, per_serve]
      Row 3: ['ENERGY (CAL)', per_100g, per_serve]
      Row 4: ['PROTEIN (G)', per_100g, per_serve]
      Row 5: ['FAT, TOTAL (G)', per_100g, per_serve]
      Row 6: ['- SATURATED (G)', per_100g, per_serve]
      Row 7: ['CARBOHYDRATES (G)', per_100g, per_serve]
      Row 8: ['- SUGARS (G)', per_100g, per_serve]
      Row 9: ['SODIUM (MG)', per_100g, per_serve]
    """
    items = []

    for page in pdf.pages:
        tables = page.extract_tables()
        if not tables:
            continue
        for table in tables:
            ct = clean_table(table)
            if len(ct) < 10:
                continue

            # Row 0 has the item name + variant
            title = ct[0][0].strip()
            if not title:
                continue

            # Parse item name and variant from title like:
            #   "AMERICAN MUSCLE SINGLE SERVED ON A WHOLEMEAL BUN"
            #   "BACON BBQ ROADSTER SERVED AS A 'LOW CARBORATOR' (LOWER CARB1)"
            name, variant = _parse_title(title)
            if not name:
                continue

            # Use "per serve" values (column 2)
            cal = safe_int(ct[3][2]) if len(ct) > 3 and len(ct[3]) > 2 else None
            protein = safe_float(ct[4][2]) if len(ct) > 4 and len(ct[4]) > 2 else None
            fat = safe_float(ct[5][2]) if len(ct) > 5 and len(ct[5]) > 2 else None
            carbs = safe_float(ct[7][2]) if len(ct) > 7 and len(ct[7]) > 2 else None
            sodium_mg = safe_float(ct[9][2]) if len(ct) > 9 and len(ct[9]) > 2 else None

            # Convert sodium mg to salt g (salt = sodium * 2.5 / 1000)
            salt = round(sodium_mg * 2.5 / 1000, 1) if sodium_mg is not None else None

            # Display name includes variant
            display_name = f"{name} ({variant})" if variant else name

            # Look up allergens from allergen PDF (match on base name)
            allergens = _lookup_allergens(allergen_map, name)

            # Dietary flags: prefer allergen PDF data, fall back to name inference
            # Don't infer gluten_free from "Gluten Free Bun" variant name --
            # the bun is GF but the burger may still contain gluten from other
            # ingredients.
            dietary_flags = _lookup_dietary(dietary_map, name)
            if dietary_flags is None:
                dietary_flags = infer_dietary_flags(name)  # use base name, not display_name

            items.append({
                "restaurant": "BurgerFuel NZ",
                "category": _categorise(name),
                "item": display_name,
                "description": "",
                "calories_kcal": cal,
                "protein_g": protein,
                "carbs_g": carbs,
                "fat_g": fat,
                "fibre_g": None,  # not in BurgerFuel PDF
                "salt_g": salt,
                "allergens": allergens,
                "dietary_flags": dietary_flags,
                "source_url": SOURCE_URL,
                "location": "National",
                "scraped_at": today,
            })

    return items


def _parse_title(title):
    """
    Parse an item title like 'AMERICAN MUSCLE SINGLE SERVED ON A WHOLEMEAL BUN'
    into (base_name, variant).

    Returns (name, variant) where variant is e.g. 'Wholemeal Bun', 'Gluten Free Bun',
    'Low Carborator', or '' if not found.
    """
    title_upper = title.upper()

    # Identify variant
    variant = ""
    split_marker = None
    if "SERVED ON A WHOLEMEAL BUN" in title_upper:
        variant = "Wholemeal Bun"
        split_marker = "SERVED ON A WHOLEMEAL BUN"
    elif "SERVED ON A GLUTEN FREE BUN" in title_upper:
        variant = "Gluten Free Bun"
        split_marker = "SERVED ON A GLUTEN FREE BUN"
    elif "LOW CARBORATOR" in title_upper:
        variant = "Low Carborator"
        split_marker = "SERVED AS A"
    elif "SERVED" in title_upper:
        split_marker = "SERVED"

    if split_marker:
        idx = title_upper.find(split_marker)
        name = title[:idx].strip()
    else:
        name = title.strip()

    # Title-case the name
    name = name.title()

    # Clean up common title-case issues
    name = name.replace("'S", "'s").replace("C N ", "C N ")

    return name, variant


def _parse_allergen_pdf(pdf):
    """
    Parse the BurgerFuel allergen/dietary suitability PDF.

    Returns:
        allergen_map: dict mapping item name (uppercase) -> list of allergen strings
        dietary_map: dict mapping item name (uppercase) -> list of dietary flag strings
    """
    allergen_map = {}
    dietary_map = {}

    # Pages 1 and 2 have menu item allergen tables (20 columns)
    for page_idx in (1, 2):
        if page_idx >= len(pdf.pages):
            continue
        tables = pdf.pages[page_idx].extract_tables()
        if not tables:
            continue
        ct = clean_table(tables[0])
        for row in ct:
            if len(row) < 16:
                continue
            name = row[0].strip().upper()
            if not name or name in ("MENU ITEM", "SUITABLE**", ""):
                continue
            # Skip category headers (col 1 has text but no allergen data pattern)
            if name.startswith("BURGERS") or name.startswith("CHICKEN") or name.startswith("KIDS"):
                continue

            # Col 8: allergens string like "Sesame, Soy, Wheat, Gluten, Milk, Egg."
            allergen_str = row[8].strip().rstrip(".")
            allergens = [a.strip().lower() for a in allergen_str.split(",") if a.strip()] if allergen_str else []

            allergen_map[name] = allergens

            # Col 9: vegetarian "Yes"/"No", Col 12: vegan "Yes"/"No"
            veg = row[9].strip().lower() if len(row) > 9 else ""
            vegan = row[12].strip().lower() if len(row) > 12 else ""

            flags = []
            if vegan == "yes":
                flags.append("vegan")
            elif veg == "yes":
                flags.append("vegetarian")
            dietary_map[name] = flags

    # Page 5: Limited Time Offers (13 columns, different layout)
    if len(pdf.pages) > 5:
        tables = pdf.pages[5].extract_tables()
        if tables:
            ct = clean_table(tables[0])
            for row in ct:
                if len(row) < 10:
                    continue
                name = row[0].strip().upper()
                if not name or name in ("LIMITED TIME OFFERS", "SUITABLE**", ""):
                    continue

                allergen_str = row[2].strip().rstrip(".") if len(row) > 2 else ""
                allergens = [a.strip().lower() for a in allergen_str.split(",") if a.strip()] if allergen_str else []
                if allergens:
                    allergen_map[name] = allergens

                veg = row[4].strip().lower() if len(row) > 4 else ""
                vegan = row[7].strip().lower() if len(row) > 7 else ""
                flags = []
                if vegan == "yes":
                    flags.append("vegan")
                elif veg == "yes":
                    flags.append("vegetarian")
                dietary_map[name] = flags

    return allergen_map, dietary_map


def _lookup_allergens(allergen_map, item_name):
    """Look up allergens with fuzzy matching."""
    name_upper = item_name.upper().strip()

    # Direct match
    if name_upper in allergen_map:
        return allergen_map[name_upper]

    # Try matching combined entries like "AMERICAN MUSCLE SINGLE / DOUBLE"
    # to either "AMERICAN MUSCLE SINGLE" or "AMERICAN MUSCLE DOUBLE"
    for key, allergens in allergen_map.items():
        if " / " in key:
            parts = [p.strip() for p in key.split(" / ")]
            # First part is full name, subsequent parts are suffixes
            base = parts[0]
            # Check if name matches base or base-prefix + any suffix
            if base == name_upper or name_upper in base or base in name_upper:
                return allergens
            # "AMERICAN MUSCLE SINGLE / DOUBLE" -> also match "AMERICAN MUSCLE DOUBLE"
            prefix = " ".join(base.split()[:-1])  # "AMERICAN MUSCLE"
            for suffix in parts[1:]:
                combined = f"{prefix} {suffix}"
                if combined == name_upper or combined in name_upper or name_upper in combined:
                    return allergens
        # Substring match
        elif key in name_upper or name_upper in key:
            return allergens

    return []


def _lookup_dietary(dietary_map, item_name):
    """Look up dietary flags with fuzzy matching, same logic as allergens."""
    name_upper = item_name.upper().strip()

    if name_upper in dietary_map:
        return dietary_map[name_upper]

    for key, flags in dietary_map.items():
        if " / " in key:
            parts = [p.strip() for p in key.split(" / ")]
            base = parts[0]
            if base == name_upper or name_upper in base or base in name_upper:
                return flags
            prefix = " ".join(base.split()[:-1])
            for suffix in parts[1:]:
                combined = f"{prefix} {suffix}"
                if combined == name_upper or combined in name_upper or name_upper in combined:
                    return flags
        elif key in name_upper or name_upper in key:
            return flags

    return None


def _safe_int(val):
    return safe_int(val)


def _safe_float(val):
    return safe_float(val)


def _fallback_data():
    """Hardcoded seed data from the BurgerFuel NZ nutritional info PDF."""
    today = str(date.today())
    raw = [
        # (category, name, kcal, protein, carbs, fat, salt_g, allergens, dietary_flags)
        ("Burgers", "American Muscle Single (Wholemeal Bun)", 992, 51.0, 64.0, 60.0, 3.3,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg", "sulphites"], []),
        ("Burgers", "American Muscle Double (Wholemeal Bun)", 1478, 90.0, 64.0, 90.0, 4.7,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg", "sulphites"], []),
        ("Burgers", "Bacon Bbq Roadster (Wholemeal Bun)", 1283, 67.0, 80.0, 69.0, 4.3,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg"], []),
        ("Burgers", "Ford Freakout (Wholemeal Bun)", 1075, 60.0, 52.0, 60.0, 3.5,
         ["sesame", "soy", "wheat", "gluten", "egg"], []),
        ("Burgers", "Bastard (Wholemeal Bun)", 1222, 67.0, 57.0, 72.0, 3.2,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg"], []),
        ("Burgers", "Bacon Backfire (Wholemeal Bun)", 885, 68.0, 29.0, 52.0, 2.7,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg"], []),
        ("Burgers", "Burnout (Wholemeal Bun)", 1003, 64.0, 49.0, 57.0, 3.2,
         ["sesame", "soy", "wheat", "gluten", "egg", "milk", "sulphites"], []),
        ("Burgers", "C N Cheese (Wholemeal Bun)", 1025, 54.0, 62.0, 58.0, 3.3,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg"], []),
        ("Burgers", "Hamburgini With Cheese (Wholemeal Bun)", 641, 39.0, 34.0, 37.0, 2.2,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg"], []),
        ("Burgers", "Bio Fuel (Wholemeal Bun)", 980, 55.0, 56.0, 55.0, 2.7,
         ["sesame", "soy", "wheat", "gluten", "egg"], []),
        ("Chicken", "Chook Royale (Wholemeal Bun)", 383, 30.0, 20.0, 17.0, 1.4,
         ["sesame", "soy", "wheat", "gluten", "egg"], []),
        ("Chicken", "Modifried Thunderbird (Wholemeal Bun)", 783, 38.0, 57.0, 40.0, 2.4,
         ["sesame", "soy", "wheat", "gluten", "egg"], []),
        ("Vegetarian", "V-Twin Vege (Wholemeal Bun)", 919, 31.0, 79.0, 46.0, 2.8,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg"], ["vegetarian"]),
        ("Vegan", "V8 Vegan (Wholemeal Bun)", 767, 20.0, 89.0, 30.0, 2.7,
         ["wheat", "gluten", "sesame", "soy", "cashews"], ["vegan"]),
        ("Kids", "Kids Cheeseburger Meal (Wholemeal Bun)", 930, 43.0, 88.0, 42.0, 2.9,
         ["sesame", "soy", "wheat", "gluten", "milk", "egg"], []),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, salt, allergens, flags in raw:
        items.append({
            "restaurant": "BurgerFuel NZ",
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
            "dietary_flags": flags if flags else infer_dietary_flags(name),
            "source_url": SOURCE_URL,
            "scraped_at": today,
        })
    print(f"  [BurgerFuelNZ] Using {len(items)} fallback items")
    return items
