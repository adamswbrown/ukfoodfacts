"""
Custom (manually added) restaurants and meals.
Stores data in output/custom_items.json, separate from scraped data.
"""

import json
from datetime import date
from pathlib import Path

CUSTOM_DB = Path(__file__).parent.parent / "output" / "custom_items.json"
PENDING_DB = Path(__file__).parent.parent / "output" / "pending_items.json"


def load():
    """Load all custom items."""
    if not CUSTOM_DB.exists():
        return []
    with open(CUSTOM_DB) as f:
        return json.load(f)


def save(items):
    """Save custom items list."""
    CUSTOM_DB.parent.mkdir(exist_ok=True)
    with open(CUSTOM_DB, "w") as f:
        json.dump(items, f, indent=2)


def add_item(restaurant, category, item_name, calories_kcal,
             protein_g=None, carbs_g=None, fat_g=None,
             fibre_g=None, salt_g=None, description="",
             location="National"):
    """Add a single custom meal item."""
    items = load()
    new_item = {
        "restaurant": restaurant.strip(),
        "category": category.strip(),
        "item": item_name.strip(),
        "description": description.strip(),
        "location": location.strip() if location else "National",
        "calories_kcal": _safe_int(calories_kcal),
        "protein_g": _safe_float(protein_g),
        "carbs_g": _safe_float(carbs_g),
        "fat_g": _safe_float(fat_g),
        "fibre_g": _safe_float(fibre_g),
        "salt_g": _safe_float(salt_g),
        "allergens": [],
        "dietary_flags": [],
        "source_url": "manual",
        "scraped_at": str(date.today()),
        "custom": True,
    }
    items.append(new_item)
    save(items)
    return new_item


def delete_item(restaurant, item_name):
    """Delete a custom item by restaurant + item name."""
    items = load()
    before = len(items)
    items = [i for i in items
             if not (i["restaurant"] == restaurant and i["item"] == item_name)]
    if len(items) == before:
        return False
    save(items)
    return True


def list_restaurants():
    """Return unique custom restaurant names."""
    items = load()
    return sorted(set(i["restaurant"] for i in items))


def scrape():
    """Return custom items (compatible with scraper interface)."""
    items = load()
    print(f"  [Custom] Loaded {len(items)} manually-added items")
    return items


def load_pending():
    """Load all pending (unreviewed) items."""
    if not PENDING_DB.exists():
        return []
    with open(PENDING_DB) as f:
        return json.load(f)


def save_pending(items):
    """Save pending items list."""
    PENDING_DB.parent.mkdir(exist_ok=True)
    with open(PENDING_DB, "w") as f:
        json.dump(items, f, indent=2)


def submit_item(restaurant, category, item_name, calories_kcal,
                protein_g=None, carbs_g=None, fat_g=None,
                fibre_g=None, salt_g=None, description="",
                location="National"):
    """Submit an item to the pending review queue."""
    pending = load_pending()
    new_item = {
        "restaurant": restaurant.strip(),
        "category": category.strip(),
        "item": item_name.strip(),
        "description": description.strip(),
        "location": location.strip() if location else "National",
        "calories_kcal": _safe_int(calories_kcal),
        "protein_g": _safe_float(protein_g),
        "carbs_g": _safe_float(carbs_g),
        "fat_g": _safe_float(fat_g),
        "fibre_g": _safe_float(fibre_g),
        "salt_g": _safe_float(salt_g),
        "allergens": [],
        "dietary_flags": [],
        "source_url": "user-submitted",
        "scraped_at": str(date.today()),
        "custom": True,
        "status": "pending",
        "submitted_at": str(date.today()),
    }
    pending.append(new_item)
    save_pending(pending)
    return new_item


def approve_item(index):
    """Approve a pending item by index — moves it to the custom DB."""
    pending = load_pending()
    if index < 0 or index >= len(pending):
        return None
    item = pending.pop(index)
    item.pop("status", None)
    item.pop("submitted_at", None)
    save_pending(pending)
    # Add to custom items
    items = load()
    items.append(item)
    save(items)
    return item


def reject_item(index):
    """Reject (delete) a pending item by index."""
    pending = load_pending()
    if index < 0 or index >= len(pending):
        return False
    pending.pop(index)
    save_pending(pending)
    return True


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
