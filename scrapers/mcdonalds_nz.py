"""
McDonald's New Zealand nutrition scraper
Scrapes the official McDonald's NZ nutritional PDF files.
"""

from datetime import date

from scrapers.pdf_utils import download_pdf, extract_tables, clean_table, safe_int, safe_float
from scrapers.dietary_utils import infer_dietary_flags

PDF_URLS = {
    "Core Food": "https://mcdonalds.co.nz/sites/mcdonalds.co.nz/files/NZ%20Core%20Food%20Menu_February%202026_0.pdf",
    "LTO": "https://mcdonalds.co.nz/sites/mcdonalds.co.nz/files/NZ%20LTO%20Menu_March%202026.pdf",
    "McCafe Drinks": "https://mcdonalds.co.nz/sites/mcdonalds.co.nz/files/NZ%20McCafe%20Beverages%20_February%202026.pdf",
    "Desserts": "https://mcdonalds.co.nz/sites/mcdonalds.co.nz/files/Desserts%20Menu%20-%20Allergen%2C%20Ingredient%20and%20Nutrition%20Information_January%202026.pdf",
    "Happy Meal": "https://mcdonalds.co.nz/sites/mcdonalds.co.nz/files/NZ%20Happy%20Meals_October%202025.pdf",
}

SOURCE_URL = "https://mcdonalds.co.nz/maccas-food/nutrition"

# Category headers that appear in the PDFs
CATEGORY_HEADERS = {
    "BEEF", "CHICKEN AND FISH", "WRAPS", "SIDES AND CONDIMENTS",
    "CONDIMENTS", "BREAKFAST", "DESSERTS", "SIDES", "DRINKS",
    "FRUIT AND SALADS", "FRIES", "McCafe", "McCAFE", "McCafé",
    "HAPPY MEAL", "LIMITED TIME OFFER", "LTO", "BEVERAGES",
    "HOT DRINKS", "COLD DRINKS", "McCafe DRINKS", "McCAFE DRINKS",
    "McCAFE FOOD", "McCafe FOOD",
}

# Allergen column names from the allergen summary pages (columns 1-21)
ALLERGEN_NAMES = [
    "gluten", "wheat", "egg", "milk", "soy", "sesame", "peanut",
    "tree_nuts",  # almond (col 8)
    "tree_nuts",  # brazil nut (col 9)
    "tree_nuts",  # cashew (col 10)
    "tree_nuts",  # hazelnut (col 11)
    "tree_nuts",  # macadamia (col 12)
    "tree_nuts",  # pecan (col 13)
    "tree_nuts",  # pine nut (col 14)
    "tree_nuts",  # pistachio (col 15)
    "tree_nuts",  # walnut (col 16)
    "fish", "crustacea", "molluscs", "sulphites", "lupin",
]

# Map from "Contains:" text to our allergen names
CONTAINS_MAP = {
    "gluten": "gluten",
    "wheat": "wheat",
    "egg": "egg",
    "eggs": "egg",
    "milk": "milk",
    "soy": "soy",
    "sesame": "sesame",
    "peanut": "peanut",
    "peanuts": "peanut",
    "tree nut": "tree_nuts",
    "tree nuts": "tree_nuts",
    "fish": "fish",
    "crustacea": "crustacea",
    "molluscs": "molluscs",
    "sulphites": "sulphites",
    "lupin": "lupin",
}


def scrape():
    print("  [McDonaldsNZ] Fetching nutrition PDFs...")
    all_items = []

    for label, url in PDF_URLS.items():
        try:
            pdf = download_pdf(url)
            items = _parse_pdf(pdf, label)
            pdf.close()
            if items:
                print(f"  [McDonaldsNZ] Scraped {len(items)} items from {label} PDF")
                all_items.extend(items)
        except Exception as e:
            print(f"  [McDonaldsNZ] Failed to scrape {label}: {e}")

    if all_items:
        # Deduplicate by item name (keep first occurrence)
        seen = set()
        deduped = []
        for item in all_items:
            key = item["item"]
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        print(f"  [McDonaldsNZ] Total: {len(deduped)} unique items")
        return deduped

    print("  [McDonaldsNZ] Using fallback data")
    return _fallback_data()


def _parse_pdf(pdf, pdf_label):
    """Parse nutrition data from a McDonald's NZ PDF."""
    today = str(date.today())
    allergen_map = _parse_allergen_pages(pdf)
    items = []

    # Determine which pages contain nutrition data (skip allergen pages and change tracker)
    nutrition_pages = _find_nutrition_pages(pdf)

    current_category = _default_category(pdf_label)

    for page_idx in nutrition_pages:
        page = pdf.pages[page_idx]
        tables = page.extract_tables()
        if not tables:
            continue

        for table in tables:
            page_items = _parse_nutrition_table(table, current_category, allergen_map, today)
            for item in page_items:
                if item.get("_category_update"):
                    current_category = item["_category_update"]
                else:
                    items.append(item)

    return items


def _find_nutrition_pages(pdf):
    """Find pages that contain nutrition data (not allergen summaries or change trackers)."""
    nutrition_pages = []
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        if not tables:
            continue
        first_row = tables[0][0] if tables[0] else []
        first_cell = str(first_row[0] or "") if first_row else ""

        # Skip allergen summary pages (25 columns with "Allergen Summary" header)
        if "Allergen Summary" in first_cell:
            continue
        # Skip change tracker pages
        if "Change Tracker" in first_cell:
            continue
        # Skip cover/title pages (no tables or single-cell tables)
        if len(first_row) <= 2 and not any(
            str(c or "") for c in first_row if c and "Energy" in str(c)
        ):
            # Check if any row has nutrition data
            has_nutrition = False
            for row in tables[0]:
                for cell in row:
                    if cell and "Energy (Cal)" in str(cell):
                        has_nutrition = True
                        break
                if has_nutrition:
                    break
            if not has_nutrition:
                continue

        nutrition_pages.append(i)
    return nutrition_pages


def _default_category(pdf_label):
    """Return a default category based on the PDF label."""
    mapping = {
        "Core Food": "Menu",
        "LTO": "Limited Time",
        "McCafe Drinks": "McCafe Drinks",
        "Desserts": "Desserts",
        "Happy Meal": "Happy Meal",
    }
    return mapping.get(pdf_label, "Menu")


def _parse_nutrition_table(table, current_category, allergen_map, today):
    """Parse a single table from a nutrition page, extracting all items."""
    results = []

    # Check first row for category header
    first_cell = str(table[0][0] or "").strip()
    if first_cell.upper() in {h.upper() for h in CATEGORY_HEADERS}:
        cat = _normalise_category(first_cell)
        results.append({"_category_update": cat})
        current_category = cat

    # Strategy: scan rows for category headers and "Avg Qty / Serve" markers.
    # Category headers can appear mid-table (not just the first row).

    i = 0
    while i < len(table):
        row = table[i]

        # Check for mid-table category headers
        cell0 = str(row[0] or "").strip()
        if cell0.upper() in {h.upper() for h in CATEGORY_HEADERS} and all(
            c is None or str(c).strip() == "" for c in row[1:]
        ):
            cat = _normalise_category(cell0)
            results.append({"_category_update": cat})
            current_category = cat
            i += 1
            continue

        # Find columns that contain "Avg Qty / Serve"
        serve_cols = []
        for ci, cell in enumerate(row):
            if cell and "Avg Qty / Serve" in str(cell):
                serve_cols.append(ci)

        if serve_cols:
            # Found item header row. Item names are in the row above,
            # in the same columns as "Avg Qty / Serve".
            name_row = table[i - 1] if i > 0 else None
            if name_row is None:
                i += 1
                continue

            # Extract item names from the name row at serve_col positions
            item_blocks = []  # list of (item_name, serve_col_idx)
            for sci in serve_cols:
                name = _extract_item_name(name_row, sci, table, i)
                if name:
                    item_blocks.append((name, sci))

            # Now extract nutrition data from subsequent rows
            nutrition = {}  # col_idx -> {label: value}
            for k in range(i + 1, min(i + 10, len(table))):
                nrow = table[k]
                for sci in serve_cols:
                    # The label is in the column before sci, or at sci-1
                    label = _find_label_in_row(nrow, sci)
                    if label and sci < len(nrow):
                        val = nrow[sci]
                        if sci not in nutrition:
                            nutrition[sci] = {}
                        nutrition[sci][label] = val

            # Build items
            for item_name, sci in item_blocks:
                nut = nutrition.get(sci, {})
                cal = safe_int(nut.get("Energy (Cal)"))
                if cal is None:
                    continue

                protein = safe_float(nut.get("Protein (g)"))
                fat = safe_float(nut.get("Fat, total (g)"))
                carbs = safe_float(nut.get("Carbohydrate (g)"))
                sodium = safe_float(nut.get("Sodium (mg)"))
                salt = round(sodium * 2.5 / 1000, 1) if sodium is not None else None

                allergens = _lookup_allergens(allergen_map, item_name, table, i)

                results.append(_make_item(
                    name=item_name,
                    category=current_category,
                    calories=cal,
                    protein=protein,
                    fat=fat,
                    carbs=carbs,
                    fibre=None,  # McDonald's NZ PDFs don't include fibre
                    salt=salt,
                    allergens=allergens,
                    today=today,
                ))

        i += 1

    return results


def _extract_item_name(name_row, serve_col, table, header_row_idx):
    """Extract the item name from the name row at or near the serve column.

    McDonald's NZ PDFs use several layouts:
    - Single item: name in the serve_col (or serve_col-1), e.g. ['...ingredients...', None, 'Big Mac®', None]
    - Multi-variant: base name in col 0, size/variant in serve_col, e.g. ['Vanilla Shake', '', 'Small', None, 'Medium', None, 'Large', None]
    - Multi-product: different product names in each serve_col pair, e.g. [..., 'McChicken®', None, 'Double McChicken®', None]
    """
    SIZE_WORDS = {"small", "medium", "large", "regular", "3 pc", "6 pc", "10 pc", "20 pc"}
    category_uppers = {h.upper() for h in CATEGORY_HEADERS}

    def _clean(text):
        if not text:
            return ""
        name = str(text).strip().split("\n")[0].strip()
        if name.upper() in category_uppers:
            return ""
        return name if len(name) < 80 else ""

    def _strip_size_suffixes(name):
        """Remove trailing size labels from a base name.
        e.g. 'Fries Small Medium Large' -> 'Fries'
        e.g. 'Chicken McNuggets® 3 pc 6 pc 10 pc 20 pc' -> 'Chicken McNuggets®'
        """
        import re
        # Remove trailing sequences of size words
        pattern = r'(?:\s+(?:Small|Medium|Large|Regular|\d+\s*pc))+\s*$'
        cleaned = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
        return cleaned if cleaned else name

    # Check the cell at serve_col position in the name row
    cell_at_col = _clean(name_row[serve_col]) if serve_col < len(name_row) else ""
    # Check the cell one column before (some layouts put name there)
    cell_before = _clean(name_row[serve_col - 1]) if serve_col > 0 and (serve_col - 1) < len(name_row) else ""

    # Get the base item name from column 0 (for size-variant items)
    base_name = _clean(name_row[0]) if name_row[0] else ""
    # Strip trailing size words from the base name
    base_name_clean = _strip_size_suffixes(base_name) if base_name else ""

    # Determine the variant/size label at this column
    variant = cell_at_col or cell_before

    # If the variant is a size word, combine with cleaned base name
    if variant and variant.lower() in SIZE_WORDS and base_name_clean:
        return f"{base_name_clean} ({variant})"

    # If the variant is a real product name (not empty, not a size), use it directly
    if variant and variant.lower() not in SIZE_WORDS:
        return variant

    # If we have a base name but no variant, the base name IS the item name
    # (single-item layout where Avg Qty / Serve is in a later column)
    if base_name_clean and not variant:
        return base_name_clean

    return None


def _find_label_in_row(row, serve_col):
    """Find the nutrition label in a row, looking at columns before serve_col."""
    # Labels are typically in column serve_col - 1
    for offset in range(1, min(4, serve_col + 1)):
        ci = serve_col - offset
        if ci >= 0 and ci < len(row):
            cell = row[ci]
            if cell and any(label in str(cell) for label in [
                "Energy (Cal)", "Protein (g)", "Fat, total (g)",
                "Saturated Fat (g)", "Carbohydrate (g)", "Sugars (g)",
                "Sodium (mg)", "Energy (kJ)", "Dietary Fibre",
            ]):
                return str(cell).strip()
    return None


def _parse_allergen_pages(pdf):
    """Parse allergen summary pages to build an allergen map."""
    allergen_map = {}

    for page in pdf.pages:
        tables = page.extract_tables()
        if not tables:
            continue
        first_cell = str(tables[0][0][0] or "") if tables[0] and tables[0][0] else ""
        if "Allergen Summary" not in first_cell:
            continue

        for row in tables[0][3:]:  # skip header rows (allergen summary, column headers, tree nut sub-headers)
            name = str(row[0] or "").strip()
            if not name:
                continue
            # Skip category headers
            if name.upper() in {h.upper() for h in CATEGORY_HEADERS}:
                continue

            allergens = []
            for col_idx, allergen_name in enumerate(ALLERGEN_NAMES):
                actual_col = col_idx + 1  # allergen data starts at column 1
                if actual_col < len(row) and row[actual_col]:
                    marker = str(row[actual_col]).strip().upper()
                    if marker == "P":
                        if allergen_name not in allergens:
                            allergens.append(allergen_name)
            if allergens:
                # Clean up name (may have line breaks from PDF layout)
                clean_name = " ".join(name.split())
                allergen_map[clean_name] = allergens

    return allergen_map


def _lookup_allergens(allergen_map, item_name, table, row_idx):
    """Look up allergens for an item, using allergen map and 'Contains:' text."""
    # Exact match
    if item_name in allergen_map:
        return list(allergen_map[item_name])

    # Try fuzzy match (item name appears in or matches a key)
    name_lower = item_name.lower()
    for key, allergens in allergen_map.items():
        key_lower = key.lower()
        # Match "Big Mac®" to "Big Mac® and Double Big Mac®"
        if name_lower in key_lower or key_lower in name_lower:
            return list(allergens)
        # Match "McCrispy Burger" to "McCrispy® and Double McCrispy®"
        # Strip ® and common suffixes for matching
        clean_name = name_lower.replace("®", "").replace("burger", "").strip()
        clean_key = key_lower.replace("®", "").replace("burger", "").strip()
        if clean_name and clean_key and (clean_name in clean_key or clean_key in clean_name):
            return list(allergens)

    # Fallback: parse "Contains:" from ingredient text in nearby rows
    return _parse_contains_text(table, row_idx)


def _parse_contains_text(table, row_idx):
    """Parse 'Contains:' allergen info from ingredient text near a row."""
    import re
    # Search nearby rows for "Contains:" text
    search_range = range(max(0, row_idx - 8), min(len(table), row_idx + 2))
    for ri in search_range:
        for cell in table[ri]:
            if cell and "Contains:" in str(cell):
                text = str(cell)
                # Find "Contains: Gluten, Wheat, Egg, Milk, Soy, Sesame."
                match = re.search(r"Contains[:\s]+([^.]+)", text)
                if match:
                    contains_text = match.group(1).lower()
                    allergens = []
                    for keyword, allergen_name in CONTAINS_MAP.items():
                        if keyword in contains_text and allergen_name not in allergens:
                            allergens.append(allergen_name)
                    return allergens
    return []


def _normalise_category(raw):
    """Normalise a category header to a display-friendly name."""
    mapping = {
        "BEEF": "Beef",
        "CHICKEN AND FISH": "Chicken & Fish",
        "WRAPS": "Wraps",
        "SIDES AND CONDIMENTS": "Sides & Condiments",
        "CONDIMENTS": "Condiments",
        "SIDES": "Sides",
        "FRIES": "Sides",
        "BREAKFAST": "Breakfast",
        "DESSERTS": "Desserts",
        "DRINKS": "Drinks",
        "FRUIT AND SALADS": "Salads",
        "HAPPY MEAL": "Happy Meal",
        "LIMITED TIME OFFER": "Limited Time",
        "LTO": "Limited Time",
        "BEVERAGES": "McCafe Drinks",
        "HOT DRINKS": "McCafe Drinks",
        "COLD DRINKS": "McCafe Drinks",
    }
    return mapping.get(raw.upper(), raw.title())


def _clean_item_name(name):
    """Post-process item name to fix common PDF extraction artifacts."""
    # Fix truncated names ending with dangling prepositions
    if name.endswith(" with") or name.endswith(" and") or name.endswith(" &"):
        name = name.rstrip(" with").rstrip(" and").rstrip(" &")
    # Fix "Wrap®" truncated to "Wrap"
    name = name.replace("Snack\nWrap", "Snack Wrap")
    return name.strip()


def _make_item(name, category, calories, protein, fat, carbs, fibre, salt, allergens, today):
    """Build a schema-compliant item dict."""
    name = _clean_item_name(name)
    return {
        "restaurant": "McDonalds NZ",
        "category": category,
        "item": name,
        "description": "",
        "calories_kcal": calories,
        "protein_g": protein,
        "carbs_g": carbs,
        "fat_g": fat,
        "fibre_g": fibre,
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
    """Hardcoded seed data from McDonald's NZ nutrition PDFs (March 2026)."""
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, salt_g, allergens
        ("Beef", "Big Mac\u00ae", 578, 28.0, 43.7, 31.1, 3.0, ["gluten", "wheat", "egg", "milk", "soy", "sesame"]),
        ("Beef", "Quarter Pounder\u00ae", 546, 32.4, 36.2, 29.6, 2.6, ["gluten", "wheat", "milk", "soy", "sesame"]),
        ("Beef", "Cheeseburger", 306, 16.3, 28.0, 13.9, 1.7, ["gluten", "wheat", "milk", "soy", "sesame"]),
        ("Beef", "Hamburger", 257, 13.5, 27.4, 9.9, 1.3, ["gluten", "wheat", "soy", "sesame"]),
        ("Beef", "Big Arch\u00ae", 1106, 53.9, 57.1, 73.2, 5.3, ["gluten", "wheat", "egg", "milk", "soy", "sesame"]),
        ("Chicken & Fish", "McChicken\u00ae", 458, 21.8, 46.8, 18.9, 3.0, ["gluten", "wheat", "egg", "soy", "sesame"]),
        ("Chicken & Fish", "Filet-o-Fish\u00ae", 346, 16.1, 35.6, 14.5, 1.6, ["gluten", "wheat", "egg", "milk", "soy", "sesame", "fish"]),
        ("Chicken & Fish", "McCrispy Burger", 445, 24.0, 56.4, 13.3, 2.7, ["gluten", "wheat", "egg", "soy", "sesame"]),
        ("Chicken & Fish", "Chicken McNuggets\u00ae (6 pc)", 312, 17.2, 20.9, 17.5, 1.6, ["gluten", "wheat"]),
        ("Wraps", "Crispy Chicken McWrap\u00ae", 495, 25.2, 56.9, 16.9, 2.8, ["gluten", "wheat", "egg"]),
        ("Breakfast", "Sausage and Egg McMuffin\u00ae", 380, 23.9, 24.2, 20.3, 1.8, ["gluten", "wheat", "egg", "milk", "soy"]),
        ("Breakfast", "Hash Brown", 144, 1.4, 12.5, 9.6, 0.7, []),
        ("Sides", "Fries (Medium)", 295, 4.6, 33.0, 15.7, 0.7, []),
        ("Desserts", "Apple Pie", 175, 2.3, 27.6, 5.4, 0.9, ["gluten", "wheat", "soy", "sulphites"]),
        ("Desserts", "Oreo\u00ae Cookie McFlurry\u00ae", 277, 6.9, 40.2, 9.4, 0.4, ["gluten", "wheat", "milk", "soy"]),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, salt, allergens in raw:
        items.append({
            "restaurant": "McDonalds NZ",
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
    print(f"  [McDonaldsNZ] Using {len(items)} fallback items")
    return items
