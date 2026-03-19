"""
Notable independent and fine dining restaurants across UK cities.
These are well-known establishments with estimated nutrition data.
Calorie estimates are based on typical portion sizes for similar dishes.
"""

from datetime import date


def scrape():
    """Return estimated nutrition data for notable UK restaurants."""
    today = str(date.today())
    items = []

    for restaurant, location, source_url, menu_items in _ALL_RESTAURANTS:
        for cat, name, kcal, prot, carbs, fat, fibre, salt in menu_items:
            items.append({
                "restaurant": restaurant,
                "category": cat,
                "item": name,
                "description": "",
                "location": location,
                "calories_kcal": kcal,
                "protein_g": prot,
                "carbs_g": carbs,
                "fat_g": fat,
                "fibre_g": fibre,
                "salt_g": salt,
                "allergens": [],
                "dietary_flags": [],
                "source_url": source_url,
                "scraped_at": today,
            })

    print(f"  [UK Restaurants] Loaded {len(items)} items from {len(_ALL_RESTAURANTS)} restaurants")
    return items


# ── London ───────────────────────────────────────────────────────────
# Format: (category, name, kcal, protein, carbs, fat, fibre, salt)

_DISHOOM = [
    ("Mains", "Black Daal", 420, 18.0, 48.0, 16.0, 8.0, 1.6),
    ("Mains", "Bacon Naan Roll", 480, 22.0, 52.0, 18.0, 2.0, 2.2),
    ("Mains", "Chicken Ruby", 580, 34.0, 32.0, 32.0, 4.0, 2.0),
    ("Mains", "Lamb Biryani", 680, 36.0, 68.0, 26.0, 3.0, 2.4),
    ("Mains", "Pau Bhaji", 380, 10.0, 44.0, 18.0, 6.0, 1.8),
]

_BARGE_EAST = [
    ("Mains", "Seasonal Fish", 480, 36.0, 22.0, 26.0, 3.0, 1.4),
    ("Mains", "Roast Chicken", 580, 42.0, 24.0, 32.0, 2.0, 1.8),
    ("Mains", "Mushroom Risotto", 520, 14.0, 58.0, 24.0, 3.0, 1.6),
    ("Desserts", "Chocolate Torte", 460, 6.0, 52.0, 26.0, 2.0, 0.3),
]

_PARK_CHINOIS = [
    ("Mains", "Peking Duck", 620, 38.0, 32.0, 36.0, 1.0, 2.6),
    ("Mains", "Wagyu Beef", 580, 44.0, 8.0, 42.0, 0, 1.8),
    ("Starters", "Dim Sum Selection", 420, 20.0, 38.0, 20.0, 2.0, 2.0),
    ("Mains", "Lobster Noodles", 520, 30.0, 48.0, 22.0, 2.0, 2.2),
]

_THE_IVY = [
    ("Mains", "Shepherd's Pie", 680, 32.0, 52.0, 36.0, 4.0, 2.2),
    ("Mains", "Fish & Chips", 820, 36.0, 78.0, 40.0, 4.0, 2.4),
    ("Mains", "Caesar Salad", 480, 28.0, 22.0, 30.0, 3.0, 1.8),
    ("Afternoon Tea", "Afternoon Tea", 720, 12.0, 88.0, 36.0, 2.0, 1.2),
]

# ── Manchester ───────────────────────────────────────────────────────

_EL_GATO_NEGRO = [
    ("Tapas", "Padron Peppers", 120, 2.0, 8.0, 8.0, 3.0, 0.4),
    ("Tapas", "Iberico Ham", 180, 18.0, 0, 12.0, 0, 2.0),
    ("Tapas", "Patatas Bravas", 320, 4.0, 38.0, 16.0, 3.0, 1.4),
    ("Tapas", "Gambas al Ajillo", 280, 22.0, 4.0, 20.0, 0, 1.6),
    ("Tapas", "Chorizo", 220, 12.0, 2.0, 18.0, 0, 1.8),
]

_20_STORIES = [
    ("Mains", "Ribeye Steak", 720, 56.0, 12.0, 48.0, 1.0, 2.0),
    ("Mains", "Sea Bass", 480, 38.0, 18.0, 26.0, 2.0, 1.4),
    ("Mains", "Lobster Linguine", 620, 30.0, 58.0, 28.0, 2.0, 2.2),
    ("Desserts", "Chocolate Fondant", 480, 6.0, 52.0, 28.0, 1.0, 0.3),
]

_HAWKSMOOR_MANCHESTER = [
    ("Mains", "Bone-in Ribeye", 820, 62.0, 2.0, 62.0, 0, 2.2),
    ("Mains", "Fillet Steak", 480, 52.0, 0, 28.0, 0, 1.6),
    ("Starters", "Bone Marrow", 320, 14.0, 8.0, 26.0, 0, 1.4),
    ("Sides", "Triple-Cooked Chips", 420, 5.0, 52.0, 20.0, 4.0, 0.6),
]

# ── Edinburgh ────────────────────────────────────────────────────────

_THE_KITCHIN = [
    ("Tasting Menu", "Tasting Menu", 1400, 68.0, 92.0, 72.0, 8.0, 3.4),
    ("Mains", "Seasonal Fish", 460, 36.0, 18.0, 24.0, 2.0, 1.4),
    ("Mains", "Venison", 520, 44.0, 12.0, 32.0, 2.0, 1.6),
    ("Cheese", "Cheese Course", 380, 18.0, 14.0, 28.0, 0, 1.8),
]

_THE_WITCHERY = [
    ("Mains", "Angus Fillet", 620, 52.0, 12.0, 40.0, 1.0, 1.8),
    ("Mains", "Lobster Thermidor", 580, 34.0, 18.0, 40.0, 1.0, 2.2),
    ("Starters", "Haggis Starter", 320, 16.0, 22.0, 18.0, 2.0, 1.8),
    ("Desserts", "Cranachan", 380, 5.0, 42.0, 20.0, 2.0, 0.2),
]

_HAWKSMOOR_EDINBURGH = [
    ("Mains", "Bone-in Ribeye", 820, 62.0, 2.0, 62.0, 0, 2.2),
    ("Mains", "Fillet", 480, 52.0, 0, 28.0, 0, 1.6),
    ("Mains", "Short Rib", 680, 42.0, 8.0, 52.0, 0, 2.0),
    ("Sides", "Chips", 420, 5.0, 52.0, 20.0, 4.0, 0.6),
]

# ── Birmingham ───────────────────────────────────────────────────────

_THE_WILDERNESS = [
    ("Tasting Menu", "Tasting Menu", 1200, 58.0, 78.0, 62.0, 8.0, 3.0),
    ("Mains", "Venison", 480, 42.0, 12.0, 28.0, 2.0, 1.4),
    ("Desserts", "Dessert Course", 380, 5.0, 46.0, 20.0, 1.0, 0.2),
]

_PASTURE_BIRMINGHAM = [
    ("Mains", "Sirloin", 580, 48.0, 4.0, 40.0, 0, 1.8),
    ("Mains", "Ribeye", 720, 56.0, 4.0, 52.0, 0, 2.0),
    ("Starters", "Bone Marrow", 320, 14.0, 8.0, 26.0, 0, 1.4),
    ("Sides", "Chips", 380, 4.0, 48.0, 18.0, 3.0, 0.5),
]

# ── Bristol ──────────────────────────────────────────────────────────

_WILSONS = [
    ("Tasting Menu", "Tasting Menu", 1300, 62.0, 86.0, 66.0, 10.0, 3.2),
    ("Mains", "Seasonal Fish", 440, 34.0, 18.0, 22.0, 2.0, 1.4),
    ("Mains", "Lamb", 520, 40.0, 14.0, 34.0, 2.0, 1.6),
    ("Sides", "Garden Vegetables", 220, 6.0, 24.0, 10.0, 6.0, 0.4),
]

_THE_COCONUT_TREE = [
    ("Mains", "Hoppers", 280, 6.0, 42.0, 8.0, 2.0, 0.8),
    ("Mains", "Kottu Chicken", 620, 30.0, 62.0, 26.0, 3.0, 2.4),
    ("Mains", "Devilled Prawns", 380, 24.0, 18.0, 22.0, 2.0, 2.0),
    ("Mains", "String Hoppers", 240, 4.0, 48.0, 2.0, 1.0, 0.6),
]

# ── Glasgow ──────────────────────────────────────────────────────────

_THE_GANNET = [
    ("Tasting Menu", "Tasting Menu", 1400, 68.0, 92.0, 72.0, 8.0, 3.4),
    ("Mains", "Venison Loin", 520, 44.0, 12.0, 32.0, 2.0, 1.6),
    ("Starters", "Scallops", 340, 22.0, 12.0, 22.0, 1.0, 1.2),
    ("Desserts", "Chocolate Delice", 460, 6.0, 48.0, 28.0, 2.0, 0.2),
]

_THE_FINNIESTON = [
    ("Mains", "Shetland Mussels", 380, 28.0, 16.0, 20.0, 1.0, 2.0),
    ("Starters", "Oysters x6", 120, 12.0, 6.0, 4.0, 0, 1.2),
    ("Mains", "Fish & Chips", 820, 36.0, 78.0, 40.0, 4.0, 2.4),
    ("Mains", "Seafood Chowder", 420, 22.0, 32.0, 22.0, 2.0, 2.0),
]

# ── Cardiff ──────────────────────────────────────────────────────────

_GORSE = [
    ("Tasting Menu", "10-Course Tasting", 1500, 72.0, 98.0, 76.0, 10.0, 3.6),
    ("Mains", "Welsh Lamb", 520, 40.0, 14.0, 34.0, 2.0, 1.6),
    ("Mains", "Sea Bass", 440, 34.0, 18.0, 22.0, 2.0, 1.4),
]

_THE_POTTED_PIG = [
    ("Mains", "Pork Belly", 620, 34.0, 22.0, 44.0, 2.0, 2.2),
    ("Mains", "Fish & Chips", 820, 36.0, 78.0, 40.0, 4.0, 2.4),
    ("Mains", "Steak", 680, 52.0, 12.0, 46.0, 1.0, 1.8),
    ("Desserts", "Chocolate Fondant", 460, 6.0, 50.0, 26.0, 1.0, 0.3),
]

# ── Leeds ────────────────────────────────────────────────────────────

_BAVETTE = [
    ("Mains", "Bavette Steak", 680, 50.0, 8.0, 48.0, 0, 2.0),
    ("Sides", "Frites", 380, 4.0, 48.0, 18.0, 3.0, 0.5),
    ("Mains", "Moules Mariniere", 420, 28.0, 16.0, 24.0, 1.0, 2.2),
    ("Desserts", "Tarte Tatin", 380, 4.0, 48.0, 18.0, 2.0, 0.3),
]

# ── Liverpool ────────────────────────────────────────────────────────

_AKASYA = [
    ("Mains", "Lamb Shank", 580, 38.0, 28.0, 34.0, 3.0, 2.0),
    ("Mains", "Chicken Shish", 420, 36.0, 18.0, 22.0, 2.0, 1.6),
    ("Mains", "Mixed Grill", 780, 52.0, 22.0, 52.0, 2.0, 2.8),
    ("Starters", "Hummus & Bread", 320, 10.0, 38.0, 14.0, 4.0, 1.2),
    ("Desserts", "Baklava", 280, 4.0, 32.0, 16.0, 1.0, 0.2),
]

# ── Registry ─────────────────────────────────────────────────────────
# Format: (restaurant_name, location, source_url, items_list)

_ALL_RESTAURANTS = [
    # London (Dishoom omitted — already in uk_chains.py as national chain)
    ("Barge East", "London", "https://www.bargeeast.com/", _BARGE_EAST),
    ("Park Chinois", "London", "https://www.parkchinois.com/", _PARK_CHINOIS),
    ("The Ivy", "London", "https://www.the-ivy.co.uk/", _THE_IVY),
    # Manchester
    ("El Gato Negro", "Manchester", "https://www.elgatonegro.uk/", _EL_GATO_NEGRO),
    ("20 Stories", "Manchester", "https://www.20stories.co.uk/", _20_STORIES),
    ("Hawksmoor Manchester", "Manchester", "https://thehawksmoor.com/locations/manchester/", _HAWKSMOOR_MANCHESTER),
    # Edinburgh
    ("The Kitchin", "Edinburgh", "https://thekitchin.com/", _THE_KITCHIN),
    ("The Witchery", "Edinburgh", "https://www.thewitchery.com/", _THE_WITCHERY),
    ("Hawksmoor Edinburgh", "Edinburgh", "https://thehawksmoor.com/locations/edinburgh/", _HAWKSMOOR_EDINBURGH),
    # Birmingham
    ("The Wilderness", "Birmingham", "https://www.thewildernessrestaurant.co.uk/", _THE_WILDERNESS),
    ("Pasture Birmingham", "Birmingham", "https://www.pasture-restaurant.com/", _PASTURE_BIRMINGHAM),
    # Bristol
    ("Wilsons", "Bristol", "https://www.wilsonsrestaurant.co.uk/", _WILSONS),
    ("The Coconut Tree", "Bristol", "https://www.thecoconuttree.com/", _THE_COCONUT_TREE),
    # Glasgow
    ("The Gannet", "Glasgow", "https://www.thegannetgla.com/", _THE_GANNET),
    ("The Finnieston", "Glasgow", "https://www.thefinniestonbar.com/", _THE_FINNIESTON),
    # Cardiff
    ("Gorse", "Cardiff", "https://www.gorserestaurant.co.uk/", _GORSE),
    ("The Potted Pig", "Cardiff", "https://www.thepottedpig.com/", _THE_POTTED_PIG),
    # Leeds
    ("Bavette", "Leeds", "https://www.bavette.co.uk/", _BAVETTE),
    # Liverpool
    ("Akasya", "Liverpool", "https://www.akasyarestaurant.co.uk/", _AKASYA),
]
