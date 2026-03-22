"""
Roll'd Australia nutrition scraper
Scrapes the official Roll'd "Nitty Gritty" nutritional information PDF.
"""

import re
from datetime import date

from scrapers.pdf_utils import download_pdf, extract_tables, clean_table, safe_int, safe_float
from scrapers.dietary_utils import infer_dietary_flags

PDF_URL = "https://rolld.com.au/wp-content/uploads/2024/12/NittyGritty_Dec2024.pdf"
SOURCE_URL = "https://rolld.com.au/nutritional-allergen-matrix/"

# Nutrient row labels -> our field names
NUTRIENT_MAP = {
    "energy (kj)": "energy_kj",
    "protein (g)": "protein_g",
    "fat (g)": "fat_g",
    "saturated fat (g)": None,  # skip
    "trans fat (g)": None,  # skip
    "carbohydrates (g)": "carbs_g",
    "sugars (g)": None,  # skip
    "dietary fibre (g)": "fibre_g",
    "sodium (mg)": "sodium_mg",
}

# Pages with nutrition tables (skip page 0 = cover, pages 10-13 = dietary/halal info)
NUTRITION_PAGES = list(range(1, 10))


def scrape():
    print("  [RolldAU] Fetching nutrition PDF...")
    try:
        pdf = download_pdf(PDF_URL)
        items = _parse_pdf(pdf)
        pdf.close()
        if items:
            print(f"  [RolldAU] Scraped {len(items)} items from PDF")
            return items
    except Exception as e:
        print(f"  [RolldAU] PDF scrape failed: {e}")

    print("  [RolldAU] Using fallback data")
    return _fallback_data()


def _parse_pdf(pdf):
    """Parse all nutrition tables from the Roll'd PDF."""
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
            if len(ct) < 4:
                continue
            parsed = _parse_transposed_table(ct, today)
            items.extend(parsed)

    return items


def _parse_transposed_table(table, today):
    """
    Parse a Roll'd transposed nutrition table.
    Row 0: category + item names (items in odd columns: 1, 3, 5, ...)
    Row 1: serving info (sometimes row 2 for sides/drinks)
    Remaining rows: nutrient label in col 0, values in odd columns (per serve)
    """
    items = []
    if len(table) < 4:
        return items

    # Extract category from first cell of row 0
    header_row = table[0]
    category_raw = header_row[0] if header_row[0] else ""
    category = _clean_category(category_raw)

    # Find item names - they're in the header row, every other column starting at 1
    # Each item has 2 cols: "Per serve" and "Per 100g"
    item_names = []
    item_cols = []  # the "per serve" column index for each item

    for col_idx in range(1, len(header_row)):
        name = header_row[col_idx].strip() if header_row[col_idx] else ""
        if name and name.lower() not in ("per serve", "per 100g", ""):
            item_names.append(name)
            item_cols.append(col_idx)

    if not item_names:
        return items

    # Find the row that starts nutrient data (look for "Energy (kj)")
    nutrient_start = None
    for i, row in enumerate(table):
        if row[0] and "energy" in row[0].lower():
            nutrient_start = i
            break

    if nutrient_start is None:
        return items

    # Build nutrient dict for each item
    for name_idx, item_name in enumerate(item_names):
        col = item_cols[name_idx]
        nutrients = {}

        for row in table[nutrient_start:]:
            label = row[0].strip().lower() if row[0] else ""
            field = NUTRIENT_MAP.get(label)
            if field is None:
                continue
            if col < len(row):
                nutrients[field] = row[col]

        # Convert energy kJ to kcal (1 kcal = 4.184 kJ)
        energy_kj = safe_float(nutrients.get("energy_kj"))
        calories = int(round(energy_kj / 4.184)) if energy_kj else None

        # Convert sodium mg to salt g
        sodium = safe_float(nutrients.get("sodium_mg"))
        salt = round(sodium * 2.5 / 1000, 1) if sodium is not None else None

        items.append({
            "restaurant": "Roll'd",
            "category": category,
            "item": _clean_item_name(item_name),
            "description": "",
            "calories_kcal": calories,
            "protein_g": safe_float(nutrients.get("protein_g")),
            "carbs_g": safe_float(nutrients.get("carbs_g")),
            "fat_g": safe_float(nutrients.get("fat_g")),
            "fibre_g": safe_float(nutrients.get("fibre_g")),
            "salt_g": salt,
            "allergens": [],
            "dietary_flags": infer_dietary_flags(item_name),
            "source_url": SOURCE_URL,
            "location": "National",
            "scraped_at": today,
        })

    return items


def _clean_category(raw):
    """Clean up the category string from the PDF header."""
    # Remove Vietnamese descriptions in quotes
    raw = re.sub(r"\u2018[^']*\u2019", "", raw)  # curly quotes
    raw = re.sub(r"'[^']*'", "", raw)
    raw = raw.strip()
    # Map to cleaner names
    cat_map = {
        "BÁNH MÌ": "Banh Mi",
        "BAO": "Bao",
        "BÚN": "Noodle Salad",
        "CƠM": "Rice Bowl",
        "NOODLE SOUP BOWLS": "Noodle Soup",
        "NOODLE SOUP CUPS": "Noodle Soup",
        "PHỞ CUP": "Pho",
        "PHỞ BOWL": "Pho",
        "SOLDIERS": "Rice Paper Rolls",
        "GỎI": "Salad",
        "BREAKFAST": "Breakfast",
        "SIDES": "Sides",
        "DRINKS": "Drinks",
        "CONDIMENTS": "Condiments",
    }
    for key, val in cat_map.items():
        if key in raw.upper() or key in raw:
            return val
    return raw.title() if raw else "Menu"


def _clean_item_name(name):
    """Clean up item name from PDF."""
    # Remove trailing size info in parens if it's just a weight
    name = re.sub(r"\s*\(\d+g\)\s*$", "", name)
    # Title case but preserve Vietnamese/brand terms
    return name.strip()


def _safe_int(val):
    return safe_int(val)


def _safe_float(val):
    return safe_float(val)


def _fallback_data():
    """Hardcoded seed data from Roll'd Nitty Gritty PDF (Dec 2024)."""
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, fibre, salt
        ("Banh Mi", "BBQ Chicken Banh Mi", 461, 31.2, 58.2, 8.7, 10.8, 4.3),
        ("Banh Mi", "Roast Pork & Crackling Banh Mi", 594, 39.0, 68.7, 17.7, 6.9, 4.1),
        ("Banh Mi", "Lemongrass Beef Banh Mi", 630, 35.7, 60.9, 25.5, 6.3, 3.3),
        ("Bao", "BBQ Chicken Bao", 217, 8.2, 22.2, 8.3, 1.4, 0.7),
        ("Bao", "Lemongrass Beef Bao", 216, 8.5, 21.4, 8.4, 1.4, 0.6),
        ("Bao", "Crispy Prawn Bao", 201, 6.1, 20.2, 8.3, 1.4, 0.5),
        ("Rice Bowl", "BBQ Chicken Rice Bowl", 478, 28.1, 58.3, 12.0, 3.6, 3.2),
        ("Rice Bowl", "Lemongrass Beef Rice Bowl", 611, 34.2, 56.9, 24.3, 3.5, 2.5),
        ("Noodle Salad", "BBQ Chicken Noodle Salad", 489, 26.4, 56.4, 8.0, 3.6, 4.3),
        ("Pho", "Beef Pho Bowl", 408, 25.8, 59.8, 5.3, 1.8, 4.5),
        ("Rice Paper Rolls", "Chicken Soldiers", 137, 5.1, 15.3, 5.5, 2.2, 0.9),
        ("Sides", "Vegetable Spring Rolls", 268, 2.5, 25.1, 17.2, 1.8, 1.0),
        ("Sides", "Sweet Potato Fries", 433, 4.5, 50.4, 22.1, 7.4, 2.0),
        ("Sides", "Crispy Chicken Ribs", 282, 29.9, 1.3, 17.3, 0.6, 1.2),
        ("Drinks", "Vietnamese Iced Coffee", 239, 2.1, 12.3, 2.5, 0.0, 0.1),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, fibre, salt in raw:
        items.append({
            "restaurant": "Roll'd",
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
            "location": "National",
            "scraped_at": today,
        })
    print(f"  [RolldAU] Using {len(items)} fallback items")
    return items
