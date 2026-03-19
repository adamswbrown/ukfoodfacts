"""
Local Northern Ireland restaurants — Bangor, Belfast, and surrounding areas.
These are independent/local-chain establishments with estimated nutrition data.
Calorie estimates are based on typical portion sizes for similar dishes.
"""

from datetime import date


def scrape():
    """Return estimated nutrition data for local NI restaurants."""
    today = str(date.today())
    items = []

    for restaurant, location, source_url, menu_items in _ALL_LOCAL:
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

    print(f"  [Local NI] Loaded {len(items)} items from {len(_ALL_LOCAL)} restaurants")
    return items


# ── Bangor, County Down ────────────────────────────────────────────────
# Format: (category, name, kcal, protein, carbs, fat, fibre, salt)

_BOAT_HOUSE = [
    ("Mains", "Pan-Seared Sea Bass", 480, 38.0, 22.0, 26.0, 3.0, 1.4),
    ("Mains", "Fillet Steak 8oz", 620, 52.0, 12.0, 40.0, 1.0, 1.8),
    ("Mains", "Lobster Thermidor", 580, 34.0, 18.0, 40.0, 1.0, 2.2),
    ("Starters", "Crab Bisque", 220, 10.0, 14.0, 14.0, 1.0, 1.6),
    ("Starters", "Scallops with Black Pudding", 320, 22.0, 16.0, 18.0, 1.0, 1.8),
    ("Desserts", "Sticky Toffee Pudding", 480, 5.0, 62.0, 24.0, 1.0, 0.6),
]

_DONEGANS = [
    ("Mains", "Beer Battered Fish & Chips", 920, 34.0, 82.0, 48.0, 4.0, 2.4),
    ("Mains", "Donegans Burger & Fries", 780, 38.0, 56.0, 42.0, 3.0, 2.2),
    ("Mains", "Chicken & Ham Pie", 680, 32.0, 48.0, 36.0, 2.0, 2.6),
    ("Mains", "Steak & Guinness Stew", 620, 36.0, 42.0, 28.0, 4.0, 2.0),
    ("Starters", "Soup of the Day & Bread", 280, 8.0, 32.0, 12.0, 3.0, 1.4),
    ("Starters", "Chicken Wings", 420, 28.0, 12.0, 28.0, 0, 2.0),
    ("Desserts", "Chocolate Fudge Cake", 520, 6.0, 64.0, 28.0, 2.0, 0.4),
]

_COQ_AND_BULL = [
    ("Mains", "Chargrilled Ribeye 10oz", 720, 56.0, 14.0, 48.0, 1.0, 2.0),
    ("Mains", "Roast Chicken Supreme", 580, 42.0, 28.0, 32.0, 3.0, 1.8),
    ("Mains", "Fish & Chips", 880, 32.0, 78.0, 46.0, 4.0, 2.2),
    ("Mains", "Caesar Salad with Chicken", 520, 34.0, 22.0, 32.0, 3.0, 1.8),
    ("Starters", "Prawn Cocktail", 280, 16.0, 8.0, 20.0, 1.0, 1.2),
    ("Desserts", "Creme Brulee", 380, 5.0, 38.0, 22.0, 0, 0.2),
]

_THE_NINES = [
    ("Mains", "Hake with Crushed Potatoes", 480, 36.0, 28.0, 22.0, 3.0, 1.4),
    ("Mains", "Bavette Steak & Fries", 680, 48.0, 40.0, 34.0, 3.0, 1.8),
    ("Mains", "Mushroom Risotto", 520, 12.0, 58.0, 24.0, 3.0, 1.6),
    ("Small Plates", "Crispy Squid", 320, 18.0, 22.0, 16.0, 1.0, 1.4),
    ("Small Plates", "Beef Croquettes", 280, 14.0, 24.0, 14.0, 1.0, 1.2),
    ("Desserts", "Tiramisu", 420, 8.0, 42.0, 24.0, 0, 0.3),
]

_TOMS_RESTAURANT = [
    ("Burgers", "Classic Burger & Fries", 820, 38.0, 58.0, 44.0, 3.0, 2.2),
    ("Burgers", "Cajun Chicken Burger", 720, 34.0, 52.0, 36.0, 2.0, 2.0),
    ("Mains", "BBQ Ribs Half Rack", 680, 42.0, 28.0, 42.0, 1.0, 2.8),
    ("Mains", "Jambalaya", 580, 28.0, 62.0, 22.0, 4.0, 2.4),
    ("Mains", "Cajun Chicken Pasta", 720, 36.0, 68.0, 30.0, 3.0, 2.2),
    ("Starters", "Loaded Nachos", 680, 20.0, 52.0, 40.0, 4.0, 2.4),
    ("Desserts", "Oreo Cheesecake", 520, 8.0, 56.0, 30.0, 1.0, 0.4),
]

_TORNA_A_SURRIENTO = [
    ("Pizza", "Margherita", 680, 26.0, 78.0, 24.0, 3.0, 2.0),
    ("Pizza", "Pepperoni", 780, 32.0, 78.0, 32.0, 3.0, 2.6),
    ("Pasta", "Spaghetti Carbonara", 720, 28.0, 72.0, 32.0, 2.0, 2.2),
    ("Pasta", "Penne Arrabbiata", 520, 16.0, 74.0, 16.0, 4.0, 1.8),
    ("Pasta", "Lasagne", 680, 32.0, 52.0, 34.0, 3.0, 2.4),
    ("Starters", "Garlic Bread", 280, 6.0, 32.0, 14.0, 1.0, 1.2),
    ("Starters", "Bruschetta", 240, 6.0, 28.0, 12.0, 2.0, 1.0),
]

_FRYING_SQUAD = [
    ("Fish", "Cod & Chips Regular", 840, 32.0, 78.0, 42.0, 4.0, 2.0),
    ("Fish", "Haddock & Chips Regular", 820, 34.0, 76.0, 40.0, 4.0, 2.0),
    ("Fish", "Fish Supper (Large)", 1080, 42.0, 98.0, 54.0, 5.0, 2.6),
    ("Sides", "Chips Regular", 420, 5.0, 54.0, 20.0, 4.0, 0.5),
    ("Sides", "Chip Shop Curry Sauce", 80, 1.0, 12.0, 3.0, 1.0, 1.0),
    ("Sides", "Battered Sausage", 320, 10.0, 22.0, 22.0, 1.0, 1.4),
    ("Sides", "Onion Rings x6", 280, 3.0, 32.0, 16.0, 2.0, 0.6),
]

_BANGLA = [
    ("Mains", "Chicken Tikka Masala", 580, 32.0, 28.0, 36.0, 3.0, 2.0),
    ("Mains", "Lamb Rogan Josh", 620, 34.0, 22.0, 40.0, 3.0, 2.2),
    ("Mains", "Chicken Balti", 520, 30.0, 24.0, 30.0, 3.0, 2.0),
    ("Mains", "Prawn Jalfrezi", 480, 26.0, 22.0, 28.0, 3.0, 2.2),
    ("Sides", "Pilau Rice", 280, 5.0, 48.0, 8.0, 1.0, 0.4),
    ("Sides", "Naan Bread", 260, 8.0, 42.0, 6.0, 2.0, 0.8),
    ("Starters", "Onion Bhaji x2", 240, 4.0, 24.0, 14.0, 2.0, 0.8),
    ("Starters", "Samosa x2", 280, 6.0, 28.0, 16.0, 2.0, 1.0),
]

_YAKS = [
    ("Mains", "Himalayan Masu (Chicken)", 540, 30.0, 32.0, 28.0, 3.0, 1.8),
    ("Mains", "Lamb Sekuwa", 580, 34.0, 18.0, 38.0, 2.0, 1.6),
    ("Mains", "Chicken Chowmein", 620, 28.0, 68.0, 24.0, 3.0, 2.2),
    ("Starters", "Momos Chicken x6", 320, 18.0, 28.0, 14.0, 2.0, 1.4),
    ("Starters", "Momos Vegetable x6", 280, 8.0, 32.0, 12.0, 3.0, 1.2),
    ("Sides", "Steamed Rice", 220, 4.0, 48.0, 1.0, 0, 0.1),
]

_TUK_TUK = [
    ("Mains", "Pad Thai Chicken", 680, 28.0, 78.0, 26.0, 3.0, 2.4),
    ("Mains", "Green Curry Chicken", 580, 26.0, 38.0, 34.0, 3.0, 2.0),
    ("Mains", "Massaman Curry Beef", 640, 30.0, 42.0, 36.0, 3.0, 2.2),
    ("Mains", "Thai Fried Rice", 520, 22.0, 62.0, 18.0, 2.0, 2.0),
    ("Starters", "Thai Spring Rolls x4", 280, 6.0, 32.0, 14.0, 2.0, 1.0),
    ("Starters", "Satay Chicken Skewers", 320, 24.0, 8.0, 22.0, 1.0, 1.4),
]

_LITTLE_WING = [
    ("Pizza", "Margherita 12\"", 680, 26.0, 78.0, 24.0, 3.0, 2.0),
    ("Pizza", "Pepperoni 12\"", 780, 32.0, 78.0, 32.0, 3.0, 2.6),
    ("Pizza", "BBQ Chicken 12\"", 740, 30.0, 80.0, 28.0, 3.0, 2.4),
    ("Pizza", "Veggie Supreme 12\"", 660, 22.0, 80.0, 22.0, 4.0, 2.0),
    ("Pasta", "Penne Arrabiata", 520, 16.0, 74.0, 16.0, 4.0, 1.8),
    ("Pasta", "Spaghetti Bolognese", 620, 28.0, 70.0, 22.0, 3.0, 2.0),
    ("Sides", "Garlic Bread", 280, 6.0, 32.0, 14.0, 1.0, 1.2),
    ("Sides", "Chicken Wings x6", 420, 28.0, 12.0, 28.0, 0, 2.0),
]

# ── Belfast ────────────────────────────────────────────────────────────

_OX_BELFAST = [
    ("Tasting Menu", "6-Course Tasting Menu", 1200, 60.0, 80.0, 60.0, 8.0, 3.0),
    ("Mains", "Aged Beef Fillet", 580, 48.0, 12.0, 36.0, 2.0, 1.6),
    ("Mains", "Monkfish with Fennel", 420, 34.0, 18.0, 22.0, 3.0, 1.4),
    ("Starters", "Crab with Apple", 280, 18.0, 14.0, 16.0, 2.0, 1.0),
    ("Desserts", "Chocolate Delice", 460, 6.0, 48.0, 28.0, 2.0, 0.2),
]

_MUDDLERS_CLUB = [
    ("Tasting Menu", "5-Course Tasting Menu", 1100, 55.0, 72.0, 56.0, 7.0, 2.8),
    ("Mains", "Aged Duck Breast", 520, 36.0, 18.0, 32.0, 2.0, 1.4),
    ("Mains", "Halibut with Leek", 440, 36.0, 16.0, 24.0, 2.0, 1.2),
    ("Starters", "Beef Tartare", 280, 22.0, 8.0, 18.0, 1.0, 1.0),
    ("Desserts", "Burnt Honey Parfait", 380, 6.0, 42.0, 20.0, 0, 0.2),
]

_COPPI = [
    ("Pasta", "Truffle Tagliatelle", 620, 18.0, 68.0, 28.0, 2.0, 1.8),
    ("Pasta", "Prawn Linguine", 580, 26.0, 66.0, 22.0, 2.0, 1.6),
    ("Pizza", "Margherita", 680, 26.0, 78.0, 24.0, 3.0, 2.0),
    ("Pizza", "Nduja & Honey", 740, 28.0, 76.0, 30.0, 3.0, 2.4),
    ("Mains", "Chicken Milanese", 720, 38.0, 48.0, 38.0, 2.0, 2.0),
    ("Starters", "Arancini x3", 340, 10.0, 36.0, 16.0, 1.0, 1.2),
]

_TRIBAL_BURGER = [
    ("Burgers", "Tribal Burger", 680, 36.0, 42.0, 38.0, 2.0, 2.0),
    ("Burgers", "Dirty Burger", 820, 40.0, 44.0, 50.0, 2.0, 2.6),
    ("Burgers", "Chicken Burger", 620, 32.0, 44.0, 30.0, 2.0, 1.8),
    ("Burgers", "Vegan Burger", 540, 16.0, 52.0, 26.0, 4.0, 1.6),
    ("Sides", "Fries", 380, 4.0, 48.0, 18.0, 3.0, 0.5),
    ("Sides", "Loaded Fries", 580, 18.0, 50.0, 32.0, 3.0, 1.8),
    ("Shakes", "Oreo Shake", 520, 10.0, 68.0, 22.0, 1.0, 0.5),
]

_MOURNE_SEAFOOD = [
    ("Mains", "Fish & Chips", 880, 34.0, 78.0, 44.0, 4.0, 2.0),
    ("Mains", "Seafood Chowder & Bread", 520, 24.0, 38.0, 28.0, 2.0, 2.2),
    ("Mains", "Grilled Sea Bass", 460, 38.0, 18.0, 24.0, 2.0, 1.4),
    ("Starters", "Dundrum Mussels", 380, 26.0, 12.0, 24.0, 1.0, 2.0),
    ("Starters", "Carlingford Oysters x6", 120, 12.0, 6.0, 4.0, 0, 1.2),
    ("Desserts", "Chocolate Fondant", 480, 6.0, 52.0, 28.0, 1.0, 0.3),
]

_YUGO = [
    ("Bowls", "Chicken Katsu Bowl", 680, 32.0, 78.0, 24.0, 3.0, 2.2),
    ("Bowls", "Teriyaki Salmon Bowl", 620, 34.0, 68.0, 22.0, 3.0, 2.0),
    ("Bowls", "Tofu & Vegetable Bowl", 480, 16.0, 62.0, 16.0, 4.0, 1.6),
    ("Bao Buns", "Crispy Chicken Bao x2", 420, 18.0, 42.0, 20.0, 2.0, 1.4),
    ("Bao Buns", "Pulled Pork Bao x2", 460, 22.0, 40.0, 22.0, 2.0, 1.6),
    ("Starters", "Gyoza x6", 320, 12.0, 28.0, 16.0, 1.0, 1.4),
    ("Sides", "Edamame", 120, 10.0, 8.0, 4.0, 4.0, 0.6),
]

# ── Registry ───────────────────────────────────────────────────────────
# Format: (restaurant_name, location, source_url, items_list)

_ALL_LOCAL = [
    # Bangor, County Down
    ("The Boat House", "Bangor, NI", "https://boathousebangor.com/", _BOAT_HOUSE),
    ("Donegans", "Bangor, NI", "https://www.donegansrestaurant.co.uk/", _DONEGANS),
    ("Coq & Bull Brasserie", "Bangor, NI", "https://www.clandeboyelodge.com/coq-and-bull", _COQ_AND_BULL),
    ("The Nines", "Bangor, NI", "https://www.tripadvisor.co.uk/Restaurant_Review-g191277-Bangor_County_Down_Northern_Ireland.html", _THE_NINES),
    ("Tom's Restaurant", "Bangor, NI", "https://www.tripadvisor.co.uk/Restaurant_Review-g191277-Bangor_County_Down_Northern_Ireland.html", _TOMS_RESTAURANT),
    ("Torna a Surriento", "Bangor, NI", "https://www.tripadvisor.co.uk/Restaurant_Review-g191277-Bangor_County_Down_Northern_Ireland.html", _TORNA_A_SURRIENTO),
    ("The Frying Squad", "Bangor, NI", "https://www.fryingsquad.com/", _FRYING_SQUAD),
    ("Bangla", "Bangor, NI", "https://www.banglabangor.co.uk/", _BANGLA),
    ("Yaks", "Bangor, NI", "https://www.tripadvisor.co.uk/Restaurant_Review-g191277-Bangor_County_Down_Northern_Ireland.html", _YAKS),
    ("Tuk Tuk Asian Bistro", "Bangor, NI", "https://www.tripadvisor.co.uk/Restaurant_Review-g191277-Bangor_County_Down_Northern_Ireland.html", _TUK_TUK),
    ("Little Wing Pizzeria", "Bangor, NI", "https://www.tripadvisor.co.uk/Restaurant_Review-g191277-Bangor_County_Down_Northern_Ireland.html", _LITTLE_WING),
    # Belfast
    ("OX", "Belfast", "https://www.oxbelfast.com/", _OX_BELFAST),
    ("The Muddlers Club", "Belfast", "https://themuddlersclub.com/", _MUDDLERS_CLUB),
    ("Coppi", "Belfast", "https://www.coppi.co.uk/", _COPPI),
    ("Tribal Burger", "Belfast", "https://tribalburger.com/", _TRIBAL_BURGER),
    ("Mourne Seafood Bar", "Belfast", "https://www.mourneseafood.com/", _MOURNE_SEAFOOD),
    ("Yugo", "Belfast", "https://www.yugobelfast.com/", _YUGO),
]
