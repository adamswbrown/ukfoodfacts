"""
Guzman y Gomez (GYG) Australia nutrition scraper.
Scrapes the official GYG nutritional & allergen guide PDF.
"""

from datetime import date

from scrapers.pdf_utils import download_pdf, extract_tables, clean_table, safe_int, safe_float
from scrapers.dietary_utils import infer_dietary_flags

PDF_URL = "https://www.guzmanygomez.com.au/wp-content/uploads/2026/03/260305_NUTRITION_ALLERGEN_GUIDE_420X297MM.pdf"
SOURCE_URL = "https://www.guzmanygomez.com.au/nutrition/"

# Pages 16–34 contain nutrition tables (0-indexed).
NUTRITION_PAGES = list(range(16, 35))

# Rows starting with these strings are not real menu items — skip them.
SKIP_PREFIXES = ("For spicy add", "For Spicy Add", "For Spicy add")


def scrape():
    print("  [GYG_AU] Fetching nutrition PDF...")
    try:
        pdf = download_pdf(PDF_URL)
        items = _parse_pdf(pdf)
        pdf.close()
        if items:
            print(f"  [GYG_AU] Scraped {len(items)} items from PDF")
            return items
    except Exception as e:
        print(f"  [GYG_AU] PDF scrape failed: {e}")

    print("  [GYG_AU] Using fallback data")
    return _fallback_data()


def _parse_pdf(pdf):
    """Parse nutrition tables from pages 16–34."""
    today = str(date.today())
    items = []

    for page_idx in NUTRITION_PAGES:
        if page_idx >= len(pdf.pages):
            break
        tables = pdf.pages[page_idx].extract_tables()
        if not tables:
            continue

        for table in tables:
            ct = clean_table(table)
            if len(ct) < 2:
                continue

            # Row 0 is the header — column 0 holds the category name.
            header = ct[0]
            category = _clean_category(header[0])

            # Validate this is a nutrition table by checking for expected columns.
            if not _is_nutrition_header(header):
                continue

            for row in ct[1:]:
                if len(row) < 11:
                    continue

                name = row[0].strip()
                if not name:
                    continue
                if any(name.startswith(p) for p in SKIP_PREFIXES):
                    continue

                cal = safe_int(row[3])
                # Skip rows where calories can't be parsed (non-data rows).
                if cal is None:
                    continue

                # Sodium (mg) -> salt (g): salt = sodium * 2.5 / 1000
                sodium = safe_float(row[10])
                salt = round(sodium * 2.5 / 1000, 1) if sodium is not None else None

                display_name = f"{category} - {name}" if _needs_category_prefix(category) else name

                items.append({
                    "restaurant": "Guzman y Gomez",
                    "category": category,
                    "item": display_name,
                    "description": "",
                    "calories_kcal": cal,
                    "protein_g": safe_float(row[4]),
                    "carbs_g": safe_float(row[7]),
                    "fat_g": safe_float(row[5]),
                    "fibre_g": safe_float(row[9]),
                    "salt_g": salt,
                    "allergens": [],
                    "dietary_flags": infer_dietary_flags(display_name),
                    "source_url": SOURCE_URL,
                    "scraped_at": today,
                })

    return items


def _clean_category(raw):
    """Clean up the category string from the table header."""
    if not raw:
        return "Menu"
    # Remove multiline junk and extra whitespace
    cat = " ".join(raw.split())
    # Strip location-specific notes in parentheses
    if "(GYG" in cat:
        cat = cat[:cat.index("(GYG")].strip()
    # Remove column header text that leaked in
    for suffix in ["SERVE SIZE", "ENERGY"]:
        if suffix in cat:
            cat = cat[:cat.index(suffix)].strip()
    return cat if cat else "Menu"


def _is_nutrition_header(header):
    """Check that a header row looks like a nutrition table."""
    joined = " ".join(str(c) for c in header).upper()
    return "ENERGY" in joined and ("CAL" in joined or "KJ" in joined)


def _needs_category_prefix(category):
    """
    Some categories are generic (e.g. 'Burrito') and items are just protein
    names ('Mild Grilled Chicken'). Prefix them for clarity.
    """
    generic_categories = {
        "BURRITO", "BOWL", "CAESAR BURRITO", "CALI BURRITO",
        "CAESAR CALI BURRITO", "ENCHILADA", "NACHOS", "NACHO FRIES",
        "QUESADILLA", "QUESADILLA PLUS", "CAESAR SALAD",
        "SOFT FLOUR TACOS (1 TACO)", "HARD TACOS (1 TACO)",
        "$3 TACO", "CRISPY CHICKEN TENDER TACO",
        "CHEESEBURGER CALI TACO",
        "LITTLE G'S BURRITO", "LITTLE G'S BOWL", "LITTLE G'S NACHOS",
        "BREKKIE BURRITO", "BIG BREKKIE BURRITO", "BREKKIE BOWL",
        "BREKKIE QUESADILLA", "BREKKIE QUESADILLA PLUS", "BREKKIE TACO",
        "MINI BURRITO", "MINI BOWL", "MINI CAESAR BURRITO",
        "MINI CALI BURRITO", "MINI CAESAR CALI BURRITO",
        "MINI ENCHILADA", "MINI NACHOS", "MINI NACHO FRIES",
        "MINI CAESAR SALAD",
        "ENCHILADA WITH CHEESE & QUESO",
        "MINI ENCHILADA WITH CHEESE & QUESO",
    }
    return category.upper() in generic_categories


def _safe_int(val):
    return safe_int(val)


def _safe_float(val):
    return safe_float(val)


def _fallback_data():
    """Hardcoded seed data from the GYG nutrition PDF (March 2026)."""
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, fibre, salt_g
        ("Burrito", "Burrito - Mild Grilled Chicken", 773, 48.3, 91.0, 23.5, 7.0, 4.9),
        ("Burrito", "Burrito - Mild Ground Beef", 828, 36.7, 93.9, 33.5, 7.9, 4.9),
        ("Burrito", "Burrito - Mild Pulled Pork", 759, 42.1, 90.4, 24.9, 7.0, 5.1),
        ("Bowl", "Bowl - Mild Grilled Chicken", 659, 43.8, 74.1, 20.5, 6.3, 4.3),
        ("Bowl", "Bowl - Mild Ground Beef", 714, 32.2, 77.0, 30.5, 7.2, 4.2),
        ("Nachos", "Nachos - Mild Grilled Chicken", 1110, 52.3, 77.7, 64.3, 11.9, 4.6),
        ("Quesadilla", "Quesadilla - Mild Cheese", 386, 16.2, 33.3, 20.6, 1.0, 1.7),
        ("Quesadilla", "Quesadilla - Mild Grilled Chicken", 458, 29.8, 33.7, 22.4, 1.0, 2.1),
        ("Soft Flour Tacos (1 Taco)", "Soft Flour Tacos (1 Taco) - Mild Grilled Chicken", 192, 15.8, 15.6, 7.1, 1.0, 1.2),
        ("Hard Tacos (1 Taco)", "Hard Tacos (1 Taco) - Mild Grilled Chicken", 186, 14.8, 13.2, 7.7, 1.7, 2.5),
        ("Fries", "Chipotle Seasoning - Large", 538, 7.9, 61.0, 27.7, 6.3, 1.8),
        ("Fries", "Chipotle Seasoning - Medium", 358, 5.3, 40.7, 18.5, 4.2, 1.2),
        ("Sides", "Black Beans", 154, 7.6, 30.4, 1.8, 11.9, 1.7),
        ("Desserts", "Soft Serve Cone", 164, 3.0, 29.3, 3.6, 0.6, 0.1),
        ("Desserts", "Churros with Chocolate Sauce", 400, 5.8, 45.4, 21.3, 1.9, 0.5),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, fibre, salt in raw:
        items.append({
            "restaurant": "Guzman y Gomez",
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
            "source_url": SOURCE_URL,
            "scraped_at": today,
        })
    print(f"  [GYG_AU] Using {len(items)} fallback items")
    return items
