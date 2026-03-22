"""
Betty's Burgers Australia nutrition scraper
Scrapes the official Betty's Burgers nutritional info and allergen PDFs from S3.
"""

import re
from datetime import date

from scrapers.pdf_utils import download_pdf, extract_tables, clean_table, safe_int, safe_float
from scrapers.dietary_utils import infer_dietary_flags

NUTRITION_PDF_URL = "https://bucket-bettys-burger-production-stack.s3.amazonaws.com/hqQxFPcrWi8RLMH0Y2JP3BlBb1zvUzvv4oSXQZP7.pdf"
ALLERGEN_PDF_URL = "https://bucket-bettys-burger-production-stack.s3.amazonaws.com/nkeDQjGl8ielMURMYW7ub5aSUrDuOk7I3gKDyund.pdf"
SOURCE_URL = "https://www.bettysburgers.com.au/nutritional-and-allergens"

# Allergen column names in order from Table 1 of the allergen PDF
# (the PDF headers are reversed text, e.g. "YRIAD" = "DAIRY")
ALLERGEN_COLS = [
    "dairy", "egg", "wheat", "barley", "rye", "oats", "soy",
    "peanut", "almond", "brazil_nut", "cashew", "hazelnut",
    "macadamia", "pecan", "pistachio", "walnut", "pine_nut",
    "onion", "garlic", "sesame", "crustacean", "mollusc",
    "lupin", "fish", "sulphites",
]

# Category headers that appear in column 0 of the nutrition PDF
CATEGORY_HEADERS = {
    "BURGERS", "SIDES", "BOWLS", "SAUCES", "DESSERTS", "BRUNCH*",
}


def _extract_kcal(energy_str):
    """
    Extract kcal from an energy string. The PDF uses kJ for most items,
    but some cold brew items include "(NNN Cal)" in the cell.
    Falls back to converting kJ -> kcal (kJ / 4.184).
    """
    if not energy_str:
        return None
    # Check for explicit Cal value like "796 kJ\n(190 Cal)"
    cal_match = re.search(r'\((\d+)\s*Cal\)', energy_str)
    if cal_match:
        return int(cal_match.group(1))
    # Otherwise convert kJ to kcal
    kj_match = re.search(r'([\d.,]+)', energy_str.replace(",", ""))
    if kj_match:
        try:
            kj = float(kj_match.group(1))
            return round(kj / 4.184)
        except ValueError:
            return None
    return None


def _strip_unit(val):
    """Remove trailing units like ' g', ' mg', ' mL' from a cell value.
    Also fixes PDF artifacts where a space appears instead of a decimal point
    (e.g. '37 7 g' -> '37.7').
    """
    if not val:
        return val
    cleaned = re.sub(r'\s*(g|mg|mL|kJ|kj)$', '', str(val).strip())
    # Fix "37 7" -> "37.7" (space-separated decimal from PDF extraction)
    cleaned = re.sub(r'^(\d+)\s+(\d+)$', r'\1.\2', cleaned)
    return cleaned


def _normalise_name(name):
    """Title-case an item name for consistency."""
    # Replace curly quotes with straight
    name = name.replace("\u2019", "'").replace("\u2018", "'")
    # Title case but keep short words lowercase
    words = name.split()
    result = []
    for i, w in enumerate(words):
        if i == 0 or w.upper() not in ("AND", "OF", "THE", "WITH", "ON", "IN", "NO"):
            result.append(w.capitalize())
        else:
            result.append(w.lower())
    return " ".join(result)


def scrape():
    print("  [BettysAU] Fetching nutrition PDF...")
    try:
        nutrition_pdf = download_pdf(NUTRITION_PDF_URL)
        allergen_pdf = download_pdf(ALLERGEN_PDF_URL)
        items = _parse_pdfs(nutrition_pdf, allergen_pdf)
        nutrition_pdf.close()
        allergen_pdf.close()
        if items:
            print(f"  [BettysAU] Scraped {len(items)} items from PDFs")
            return items
    except Exception as e:
        print(f"  [BettysAU] PDF scrape failed: {e}")

    print("  [BettysAU] Using fallback data")
    return _fallback_data()


def _parse_pdfs(nutrition_pdf, allergen_pdf):
    """Parse the nutrition and allergen PDFs into item dicts."""
    today = str(date.today())
    allergen_map = _parse_allergens(allergen_pdf)
    items = []

    tables = nutrition_pdf.pages[0].extract_tables()
    if not tables:
        return items

    ct = clean_table(tables[0])
    current_category = "Menu"

    for row in ct:
        if len(row) < 17:
            continue

        # Column 0 holds category labels (only on first row of each section)
        cat_cell = (row[0] or "").strip().replace("\n", " ")
        if cat_cell:
            # Clean up multi-line category names like "SOFT\nDRINKS"
            cat_clean = cat_cell.upper()
            if cat_clean in ("SOFT DRINKS",):
                current_category = "Soft Drinks"
            elif cat_clean in ("THICK SHAKES",):
                current_category = "Thick Shakes"
            elif cat_clean in ("COLD BREW",):
                current_category = "Cold Brew"
            elif cat_clean == "BRUNCH*":
                current_category = "Brunch"
            else:
                current_category = cat_clean.title()

        name_raw = (row[1] or "").strip()
        if not name_raw:
            continue

        # Skip header rows
        name_upper = name_raw.upper()
        if name_upper in ("PRODUCT", "ITEM") or name_upper.startswith("INFORMATION"):
            continue
        # Skip rows that match category headers appearing in col 1
        if name_upper in ("AVE. QTY", "AVE. QTY\n/SERVE"):
            continue

        # Energy is in column 3 (per serve), in kJ (or kJ with Cal annotation)
        energy_str = (row[3] or "").strip()
        kcal = _extract_kcal(energy_str)
        if kcal is None:
            continue  # skip non-data rows

        protein = safe_float(_strip_unit(row[5]))
        fat = safe_float(_strip_unit(row[7]))
        carbs = safe_float(_strip_unit(row[11]))
        # No fibre column in this PDF
        sodium_mg = safe_float(_strip_unit(row[15]))
        salt = round(sodium_mg * 2.5 / 1000, 1) if sodium_mg is not None else None

        display_name = _normalise_name(name_raw)
        allergens = _lookup_allergens(allergen_map, name_raw, category=current_category)
        dietary_flags = infer_dietary_flags(display_name)

        # Cross-check: remove vegan/vegetarian flags if allergens contradict
        if allergens:
            has_dairy_egg = any(a in allergens for a in ("dairy", "egg"))
            has_meat_fish = any(a in allergens for a in ("fish", "crustacean", "mollusc"))
            if "vegan" in dietary_flags and (has_dairy_egg or has_meat_fish):
                dietary_flags.remove("vegan")
            if "vegetarian" in dietary_flags and has_meat_fish:
                dietary_flags.remove("vegetarian")

        items.append({
            "restaurant": "Betty's Burgers",
            "category": current_category,
            "item": display_name,
            "description": "",
            "calories_kcal": kcal,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "fibre_g": None,
            "salt_g": salt,
            "allergens": allergens,
            "dietary_flags": dietary_flags,
            "source_url": SOURCE_URL,
            "scraped_at": today,
        })

    return items


def _parse_allergens(allergen_pdf):
    """
    Parse the allergen PDF (Table 1) into a dict: item_name_upper -> list of allergen strings.
    Table 1 is the structured table with clear rows per item.
    """
    allergen_map = {}
    tables = allergen_pdf.pages[0].extract_tables()
    if not tables or len(tables) < 2:
        return allergen_map

    # Table 1 is the main structured allergen table
    ct = clean_table(tables[1])
    for row in ct:
        if len(row) < 26:
            continue
        name = (row[0] or "").strip().replace("\n", " ")
        if not name:
            continue
        # Skip category headers and header rows
        name_key = _normalise_key(name)
        if name_key in ("BURGERS", "SIDES", "ADD-ONS", "SAUCES", "BOWLS", ""):
            continue
        # Skip reversed-text header row
        if "YRIAD" in name_key or "TAEHW" in name_key:
            continue

        allergens = []
        for i, allergen_name in enumerate(ALLERGEN_COLS):
            col_idx = i + 1  # allergen data starts at column 1
            if col_idx < len(row) and (row[col_idx] or "").strip().lower() == "x":
                allergens.append(allergen_name)
        allergen_map[name_key] = allergens

    # Also parse Table 2 (ice cream, thick shakes, desserts) with fewer columns
    if len(tables) >= 3:
        ice_cream_cols = ["dairy", "egg", "wheat", "soy", "peanut", "barley", "hazelnut", "lupin", "sesame"]
        ct2 = clean_table(tables[2])
        current_sub = ""
        for row in ct2:
            if len(row) < 10:
                continue
            name = (row[0] or "").strip()
            if not name:
                continue
            name_key = _normalise_key(name)
            if name_key in ("ICE CREAM", "THICK SHAKES", "DESSERTS"):
                current_sub = name_key
                continue
            if "YRIAD" in name_key:
                continue

            allergens = []
            for i, allergen_name in enumerate(ice_cream_cols):
                col_idx = i + 1
                if col_idx < len(row) and (row[col_idx] or "").strip().lower() == "x":
                    allergens.append(allergen_name)

            # Disambiguate duplicate names (e.g. "VANILLA" appears in ice cream and shakes)
            key = name_key
            if current_sub == "THICK SHAKES":
                key = name_key + " (SHAKE)"
            elif current_sub == "ICE CREAM":
                key = name_key + " (ICE CREAM)"
            allergen_map[key] = allergens

    return allergen_map


def _normalise_key(name):
    """Normalise a name for allergen map lookup: uppercase, straight quotes."""
    return name.strip().upper().replace("\u2019", "'").replace("\u2018", "'").replace("\u2019", "'")


def _lookup_allergens(allergen_map, item_name, category=""):
    """Look up allergens by item name with fuzzy matching."""
    name_upper = _normalise_key(item_name)

    # Direct match
    if name_upper in allergen_map:
        return allergen_map[name_upper]

    # Try matching thick shakes and ice cream by suffixed key based on category
    cat_upper = category.upper()
    if cat_upper == "THICK SHAKES":
        key = name_upper + " (SHAKE)"
        if key in allergen_map:
            return allergen_map[key]
    elif cat_upper == "DESSERTS":
        # Desserts in nutrition PDF are froyo items — no suffix needed, already in map
        pass

    # Special mappings for items with different names between PDFs
    name_mapping = {
        "BETTY'S SPECIAL SAUCE": "BETTY'S SAUCE",
        "CRISPY STRIPS": "CRISPY CHICKEN STRIPS",
        "NOOSA CLASSIC SURF": "NOOSA SURF CLASSIC",
        "CRISPY CHICKEN SUPREME": "CHICKEN SUPREME",
        "GRILLED CHICKEN SUPREME": "CHICKEN SUPREME",
        "GRILLED CHICKEN BARE": "BARE BETTY",
        "THREE CHEESE BURGER": "CHEESEBURGER",
        "CHICKEN, AVO, BACON BOWL": "GRILLED CHICKEN, AVO, BACON BOWL",
        "SALMON BOWL": "GRILLED SALMON SUPER BOWL",
        "VEGE PATTY SUPER BOWL": "VEG PATTY SUPER BOWL",
        "SPICY VEGAN": "VEGAN SPICY MAYO",
        "SPICY GRILLED CHICKEN": "SPICY CHICKEN",
    }
    mapped = name_mapping.get(name_upper)
    if mapped and mapped in allergen_map:
        return allergen_map[mapped]

    # Partial match: prefer longest matching key to avoid "BETTY'S CLASSIC"
    # matching "BETTY'S CLASSIC VEGAN"
    best_match = None
    best_len = 0
    for key, allergens in allergen_map.items():
        clean_key = key.replace(" (SHAKE)", "").replace(" (ICE CREAM)", "")
        if clean_key == name_upper:
            return allergens
        if len(clean_key) > 4 and clean_key in name_upper and len(clean_key) > best_len:
            best_match = allergens
            best_len = len(clean_key)
        if len(name_upper) > 4 and name_upper in clean_key and len(name_upper) > best_len:
            best_match = allergens
            best_len = len(name_upper)

    if best_match is not None:
        return best_match

    return []


def _safe_int(val):
    return safe_int(val)


def _safe_float(val):
    return safe_float(val)


def _fallback_data():
    """Hardcoded seed data from the Betty's Burgers nutritional PDF."""
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, salt_g, allergens
        ("Burgers", "Bare Betty", 324, 24.7, 9.2, 21.1, 1.6, ["dairy", "egg", "soy", "onion", "garlic"]),
        ("Burgers", "Betty's Classic", 603, 28.5, 32.9, 39.9, 2.1, ["dairy", "egg", "wheat", "soy", "onion", "garlic"]),
        ("Burgers", "Betty's Classic Vegan", 875, 9.2, 86.7, 54.8, 3.3, ["soy", "onion", "garlic", "sesame"]),
        ("Burgers", "Betty's Deluxe", 685, 38.0, 44.0, 41.5, 3.9, ["dairy", "egg", "wheat", "soy", "onion", "garlic"]),
        ("Burgers", "Betty's Double", 882, 59.3, 42.8, 52.8, 5.2, ["dairy", "egg", "wheat", "soy", "onion", "garlic"]),
        ("Burgers", "Crispy Chicken", 625, 29.7, 43.1, 37.2, 2.4, ["wheat", "onion", "garlic", "crustacean", "mollusc"]),
        ("Burgers", "Grilled Chicken", 397, 31.8, 26.2, 18.2, 1.3, ["garlic"]),
        ("Burgers", "Shroom Burger", 656, 19.7, 77.5, 33.7, 3.3, ["dairy", "egg", "wheat", "soy", "onion", "garlic", "crustacean", "mollusc"]),
        ("Burgers", "Spicy Chicken", 738, 43.1, 49.8, 40.9, 4.2, ["dairy", "egg", "wheat", "soy", "onion", "garlic", "crustacean", "mollusc"]),
        ("Sides", "Fries", 386, 4.9, 49.8, 18.4, 1.4, ["soy", "sesame"]),
        ("Sides", "Sweet Potato Fries", 338, 4.4, 46.6, 16.4, 1.3, ["soy", "sesame"]),
        ("Sides", "Onion Rings", 377, 3.4, 30.1, 27.2, 1.5, ["dairy", "egg", "wheat", "soy", "onion", "crustacean", "mollusc"]),
        ("Sides", "Calamari", 190, 13.8, 9.5, 10.8, 1.1, ["wheat", "garlic", "crustacean", "mollusc"]),
        ("Thick Shakes", "Chocolate", 569, 17.4, 104.7, 13.7, 0.5, ["dairy", "egg"]),
        ("Desserts", "Chocolate Deluxe", 472, 2.1, 39.9, 19.8, 2.2, ["dairy", "egg", "soy", "barley", "hazelnut"]),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, salt, allergens in raw:
        items.append({
            "restaurant": "Betty's Burgers",
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
    print(f"  [BettysAU] Using {len(items)} fallback items")
    return items
