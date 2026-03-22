"""
Burger King New Zealand nutrition scraper
Scrapes the official BK NZ nutritional guide PDF.
"""

from datetime import date

from scrapers.pdf_utils import download_pdf, extract_tables, clean_table, safe_int, safe_float
from scrapers.dietary_utils import infer_dietary_flags

PDF_URL = "https://bknzpublic.z8.web.core.windows.net/nutritionalguide/nutritionalguide.pdf"
SOURCE_URL = "https://www.burgerking.co.nz/menu"

# Allergen column names in order (from the rotated headers on page 2)
ALLERGEN_COLS = [
    "peanut", "tree_nuts", "sesame", "milk", "eggs", "fish",
    "crustacean", "mollusc", "soy", "gluten", "wheat",
    "sulphites", "lupin", "other",
]

# Category labels in col 0 are rotated text and come out garbled.
# We assign categories based on known item ranges instead.
CATEGORY_KEYWORDS = {
    "whopper": "Burgers",
    "cheeseburger": "Burgers",
    "hamburger": "Burgers",
    "double cheese": "Burgers",
    "triple cheese": "Burgers",
    "creamy mayo": "Burgers",
    "bbq rodeo": "Burgers",
    "bbq bacon": "Burgers",
    "the bomb": "Burgers",
    "xl ": "Burgers",
    "steakhouse": "Burgers",
    "salad burger": "Burgers",
    "mega stacker": "Burgers",
    "plant based": "Plant Based",
    "nugget": "Chicken",
    "bk chicken": "Chicken",
    "crispy chicken": "Chicken",
    "fried chicken": "Chicken",
    "chicken fries": "Chicken",
    "fries": "Sides",
    "hash bites": "Sides",
    "king box": "Sides",
    "onion rings": "Sides",
    "curly fries": "Sides",
    "coke": "Drinks",
    "fanta": "Drinks",
    "frozen": "Drinks",
    "shake": "Drinks",
    "super shake": "Drinks",
    "keri": "Drinks",
    "sundae": "Desserts",
    "soft serve": "Desserts",
    "cookie": "Desserts",
    "fusion": "Desserts",
    "popping candy": "Desserts",
    "wild berry": "Desserts",
    "tropical": "Limited Time",
}


def _categorise(item_name):
    """Assign a category based on item name keywords."""
    name_lower = item_name.lower()
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in name_lower:
            return category
    return "Menu"


def scrape():
    print("  [BurgerKingNZ] Fetching nutrition PDF...")
    try:
        pdf = download_pdf(PDF_URL)
        items = _parse_pdf(pdf)
        pdf.close()
        if items:
            print(f"  [BurgerKingNZ] Scraped {len(items)} items from PDF")
            return items
    except Exception as e:
        print(f"  [BurgerKingNZ] PDF scrape failed: {e}")

    print("  [BurgerKingNZ] Using fallback data")
    return _fallback_data()


def _parse_pdf(pdf):
    """Parse both nutrition pages and the allergen page."""
    today = str(date.today())
    items = []

    # --- Parse allergen data from page 2 ---
    allergen_map = _parse_allergens(pdf)

    # --- Page 0: Core menu (19 columns, no size column) ---
    tables0 = pdf.pages[0].extract_tables()
    if tables0:
        ct = clean_table(tables0[0])
        for row in ct:
            if len(row) < 19:
                continue
            name = row[1].strip()
            if not name or name == "PRODUCT" or name.startswith("Information"):
                continue
            # Page 0 columns (per serve):
            # 0=category, 1=item, 2=serving_g, 3=energy_kj, 4=energy_kcal,
            # 5=protein, 6=fat, 7=sat_fat, 8=carbs, 9=sugars, 10=sodium_mg
            cal = safe_int(row[4])
            if cal is None and safe_int(row[3]) is None:
                continue  # skip non-data rows

            allergens = _lookup_allergens(allergen_map, name)
            items.append(_make_item(
                name=name,
                category=_categorise(name),
                calories=cal,
                protein=row[5],
                fat=row[6],
                carbs=row[8],
                fibre=None,  # BK NZ PDF doesn't include fibre
                sodium_mg=row[10],
                allergens=allergens,
                today=today,
            ))

    # --- Page 1: Drinks, Desserts & Limited Time (20 columns, has size column) ---
    if len(pdf.pages) > 1:
        tables1 = pdf.pages[1].extract_tables()
        if tables1:
            ct = clean_table(tables1[0])
            current_item = None
            for row in ct:
                if len(row) < 20:
                    continue
                name = row[1].strip()
                size = row[2].strip() if row[2] else ""

                # Track current item name (sizes share the name from above)
                if name:
                    current_item = name
                elif current_item and size:
                    name = current_item
                else:
                    continue

                if name == "PRODUCT" or name.startswith("Information"):
                    continue

                # Page 1 columns (per serve):
                # 0=category, 1=item, 2=size, 3=serving_g, 4=energy_kj, 5=energy_kcal,
                # 6=protein, 7=fat, 8=sat_fat, 9=carbs, 10=sugars, 11=sodium_mg
                cal = safe_int(row[5])
                if cal is None and safe_int(row[4]) is None:
                    continue

                display_name = f"{name} ({size})" if size else name
                allergens = _lookup_allergens(allergen_map, name)

                items.append(_make_item(
                    name=display_name,
                    category=_categorise(name),
                    calories=cal,
                    protein=row[6],
                    fat=row[7],
                    carbs=row[9],
                    fibre=None,
                    sodium_mg=row[11],
                    allergens=allergens,
                    today=today,
                ))

    return items


def _parse_allergens(pdf):
    """Parse allergen page (page 2) into a dict: item_name -> list of allergen strings."""
    allergen_map = {}
    if len(pdf.pages) < 3:
        return allergen_map

    tables = pdf.pages[2].extract_tables()
    if not tables:
        return allergen_map

    ct = clean_table(tables[0])
    for row in ct:
        if len(row) < 16:
            continue
        name = row[1].strip()
        if not name or name.startswith("Information") or name == "PRODUCT":
            continue

        allergens = []
        for i, allergen_name in enumerate(ALLERGEN_COLS):
            col_idx = i + 2  # allergen data starts at column 2
            if col_idx < len(row) and row[col_idx].lower() == "yes":
                allergens.append(allergen_name)
        if allergens:
            allergen_map[name] = allergens

    return allergen_map


def _lookup_allergens(allergen_map, item_name):
    """Look up allergens with fuzzy matching for 'Range' entries."""
    if item_name in allergen_map:
        return allergen_map[item_name]
    # Try matching "WHOPPER® Range" to "WHOPPER® Double" etc.
    name_lower = item_name.lower()
    for key, allergens in allergen_map.items():
        key_base = key.replace(" Range", "").replace(" range", "")
        if key_base.lower() in name_lower or name_lower in key_base.lower():
            return allergens
    return []


def _make_item(name, category, calories, protein, fat, carbs, fibre, sodium_mg, allergens, today):
    """Build a schema-compliant item dict."""
    # Convert sodium mg to salt g (salt = sodium * 2.5 / 1000)
    sodium = safe_float(sodium_mg)
    salt = round(sodium * 2.5 / 1000, 1) if sodium is not None else None

    return {
        "restaurant": "Burger King NZ",
        "category": category,
        "item": name,
        "description": "",
        "calories_kcal": safe_int(calories) if isinstance(calories, (str, int, float)) else calories,
        "protein_g": safe_float(protein),
        "carbs_g": safe_float(carbs),
        "fat_g": safe_float(fat),
        "fibre_g": safe_float(fibre),
        "salt_g": salt,
        "allergens": allergens,
        "dietary_flags": infer_dietary_flags(name),
        "source_url": SOURCE_URL,
        "scraped_at": today,
    }


def _safe_int(val):
    return safe_int(val)


def _safe_float(val):
    return safe_float(val)


def _fallback_data():
    """Hardcoded seed data from the BK NZ nutritional guide PDF (March 2026)."""
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, salt_g, allergens
        ("Burgers", "WHOPPER Jr\u00ae", 361, 16.2, 23.8, 20.2, 1.1, ["sesame", "eggs", "soy", "gluten", "wheat"]),
        ("Burgers", "WHOPPER\u00ae", 764, 37.6, 40.8, 46.1, 2.6, ["sesame", "eggs", "soy", "gluten", "wheat"]),
        ("Burgers", "WHOPPER\u00ae with Cheese", 808, 39.6, 41.1, 49.2, 3.0, ["sesame", "milk", "eggs", "soy", "gluten", "wheat"]),
        ("Burgers", "Cheeseburger", 349, 18.1, 24.6, 17.4, 1.5, ["sesame", "milk", "eggs", "soy", "gluten", "wheat"]),
        ("Burgers", "Double Cheeseburger", 519, 32.7, 25.2, 29.3, 2.1, ["sesame", "milk", "eggs", "soy", "gluten", "wheat"]),
        ("Burgers", "Hamburger", 302, 16.0, 24.2, 14.2, 1.1, ["sesame", "eggs", "soy", "gluten", "wheat"]),
        ("Chicken", "Chicken Nuggets - 10pk", 488, 22.3, 30.2, 29.5, 1.6, ["soy", "gluten", "wheat"]),
        ("Chicken", "BK Chicken", 547, 22.7, 39.2, 32.8, 2.0, ["sesame", "milk", "eggs", "soy", "gluten", "wheat"]),
        ("Chicken", "Crispy Chicken Burger", 520, 14.1, 35.5, 34.7, 1.4, ["milk", "eggs", "soy", "gluten", "wheat"]),
        ("Sides", "Thick Cut Fries - Regular", 162, 2.0, 21.3, 7.2, 0.2, ["gluten", "wheat"]),
        ("Sides", "Onion Rings - 6 pack", 237, 2.8, 27.1, 12.5, 0.7, ["milk", "soy", "gluten", "wheat"]),
        ("Plant Based", "Plant Based Whopper", 556, 22.1, 45.7, 28.5, 2.3, ["sesame", "soy", "gluten", "wheat"]),
        ("Desserts", "Soft Serve Cone", 154, 3.7, 24.3, 4.2, 0.2, ["milk"]),
        ("Desserts", "Chocolate Sundae", 316, 5.5, 44.1, 12.4, 0.3, ["milk", "soy"]),
        ("Drinks", "Chocolate Shake (Small)", 310, 6.4, 47.1, 9.9, 0.3, ["milk"]),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, salt, allergens in raw:
        items.append({
            "restaurant": "Burger King NZ",
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
            "dietary_flags": infer_dietary_flags(name),
            "source_url": SOURCE_URL,
            "scraped_at": today,
        })
    print(f"  [BurgerKingNZ] Using {len(items)} fallback items")
    return items
