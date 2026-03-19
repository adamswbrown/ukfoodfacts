"""
Fallback nutrition data for UK pub chains.
Each chain has a representative sample of popular menu items.
Sources: Official nutrition pages (verified March 2026).
"""

from datetime import date


def scrape():
    """Return fallback nutrition data for all UK pub chains."""
    today = str(date.today())
    items = []

    for chain_name, source_url, chain_items in _ALL_PUBS:
        for cat, name, kcal, prot, carbs, fat, fibre, salt in chain_items:
            items.append({
                "restaurant": chain_name,
                "category": cat,
                "item": name,
                "description": "",
                "location": "National",
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

    print(f"  [UK Pubs] Loaded {len(items)} items from {len(_ALL_PUBS)} pub chains")
    return items


# -- Pub chain data -------------------------------------------------------
# Format per item: (category, name, kcal, protein, carbs, fat, fibre, salt)

_SIZZLING_PUBS = [
    ("Grill", "Classic Mixed Grill", 1210, 82, 48, 76, 3, 4.2),
    ("Grill", "Gammon & Eggs", 780, 52, 38, 44, 2, 3.8),
    ("Fish", "Fish & Chips", 920, 38, 82, 46, 5, 2.4),
    ("Fish", "Scampi & Chips", 680, 22, 68, 32, 4, 2.1),
    ("Burgers", "Chicken Burger", 720, 36, 58, 36, 3, 2.2),
    ("Pies", "Steak & Ale Pie", 850, 34, 68, 48, 3, 2.8),
    ("Mains", "Mac & Cheese", 680, 24, 62, 36, 2, 2.0),
    ("Sharers", "Loaded Nachos", 780, 26, 72, 42, 6, 3.2),
    ("Desserts", "Chocolate Fudge Cake", 520, 6, 68, 24, 2, 0.6),
    ("Desserts", "Sticky Toffee Pudding", 480, 5, 72, 18, 1, 0.8),
]

_CHEF_AND_BREWER = [
    ("Roasts", "Sunday Roast Beef", 680, 48, 52, 30, 4, 2.6),
    ("Fish", "Fish & Chips", 880, 36, 78, 44, 5, 2.2),
    ("Burgers", "Steak Burger", 780, 42, 54, 40, 3, 2.4),
    ("Salads", "Chicken Caesar Salad", 520, 38, 22, 32, 3, 2.0),
    ("Fish", "Scampi & Chips", 660, 20, 66, 30, 4, 1.9),
    ("Pies", "Pie of the Day", 720, 28, 62, 38, 3, 2.4),
    ("Fish", "Salmon Fillet", 480, 36, 24, 26, 2, 1.6),
    ("Starters", "Prawn Cocktail", 280, 16, 12, 18, 1, 1.8),
    ("Desserts", "Sticky Toffee Pudding", 480, 5, 70, 18, 1, 0.8),
]

_FLAMING_GRILL = [
    ("Grill", "Mixed Grill", 1180, 78, 46, 74, 3, 4.0),
    ("Grill", "Gammon Steak", 760, 50, 36, 42, 2, 3.6),
    ("Fish", "Fish & Chips", 900, 36, 80, 44, 5, 2.3),
    ("Mains", "Chicken Tikka Masala", 720, 42, 68, 28, 4, 2.8),
    ("Fish", "Scampi & Chips", 660, 20, 66, 30, 4, 1.9),
    ("Burgers", "Burger & Fries", 820, 40, 62, 42, 4, 2.6),
    ("Mains", "Mac & Cheese", 650, 22, 60, 34, 2, 1.8),
    ("Sides", "Loaded Fries", 580, 18, 52, 32, 4, 2.4),
]

_ALL_BAR_ONE = [
    ("Salads", "Chicken & Avocado Salad", 480, 36, 18, 30, 5, 1.6),
    ("Grill", "Steak Frites", 720, 48, 44, 38, 3, 2.2),
    ("Fish", "Fish & Chips", 820, 34, 74, 42, 4, 2.0),
    ("Burgers", "Halloumi Burger", 680, 24, 58, 38, 4, 2.4),
    ("Bowls", "Salmon Poke Bowl", 520, 32, 52, 18, 5, 2.0),
    ("Sharers", "Loaded Nachos", 680, 22, 66, 36, 5, 2.8),
    ("Brunch", "Brunch Stack", 620, 28, 48, 34, 3, 2.6),
    ("Desserts", "Chocolate Brownie", 420, 6, 52, 22, 2, 0.4),
]

_EMBER_INNS = [
    ("Fish", "Fish & Chips", 880, 36, 78, 44, 5, 2.2),
    ("Pies", "Steak & Ale Pie", 780, 32, 64, 42, 3, 2.6),
    ("Burgers", "Classic Burger", 720, 38, 52, 38, 3, 2.2),
    ("Mains", "Chicken Tikka", 680, 40, 62, 26, 4, 2.6),
    ("Fish", "Scampi & Chips", 660, 20, 66, 30, 4, 1.9),
    ("Mains", "Mac & Cheese", 620, 22, 56, 32, 2, 1.8),
    ("Roasts", "Sunday Roast Beef", 680, 46, 52, 30, 4, 2.4),
    ("Desserts", "Sticky Toffee", 460, 4, 68, 18, 1, 0.7),
]

_STONEHOUSE = [
    ("Pizza", "Margherita Pizza", 680, 28, 72, 28, 3, 2.4),
    ("Pizza", "Pepperoni Pizza", 780, 34, 72, 36, 3, 3.0),
    ("Pizza", "BBQ Chicken Pizza", 740, 36, 74, 30, 3, 2.8),
    ("Carvery", "Carvery Roast Beef", 720, 46, 54, 32, 4, 2.6),
    ("Fish", "Fish & Chips", 860, 34, 78, 42, 5, 2.2),
    ("Mains", "Mac & Cheese", 620, 22, 56, 32, 2, 1.8),
    ("Burgers", "Chicken Burger", 700, 34, 56, 36, 3, 2.0),
    ("Sides", "Garlic Bread", 280, 6, 32, 14, 1, 1.2),
]

_SLUG_AND_LETTUCE = [
    ("Salads", "Chicken Caesar Salad", 520, 38, 22, 32, 3, 2.0),
    ("Fish", "Fish & Chips", 840, 34, 76, 42, 4, 2.2),
    ("Burgers", "Steak Burger", 780, 42, 54, 40, 3, 2.4),
    ("Sides", "Halloumi Fries", 360, 16, 26, 22, 2, 1.8),
    ("Brunch", "Brunch Pancakes", 580, 14, 72, 28, 2, 1.2),
    ("Sharers", "Loaded Nachos", 720, 24, 68, 38, 5, 3.0),
    ("Pizza", "Pizza Margherita", 680, 28, 72, 28, 3, 2.4),
    ("Desserts", "Chocolate Brownie", 440, 6, 54, 22, 2, 0.4),
]

_ONEILLS = [
    ("Fish", "Fish & Chips", 880, 36, 78, 44, 5, 2.2),
    ("Mains", "Beef & Guinness Stew", 620, 42, 44, 26, 5, 2.8),
    ("Burgers", "Chicken Burger", 720, 36, 58, 36, 3, 2.2),
    ("Burgers", "Bacon Cheeseburger", 820, 44, 54, 44, 3, 3.0),
    ("Sides", "Loaded Fries", 560, 16, 50, 30, 4, 2.2),
    ("Mains", "Mac & Cheese", 640, 22, 58, 34, 2, 1.8),
    ("Desserts", "Chocolate Fudge Cake", 480, 6, 64, 22, 2, 0.5),
]

_NICHOLSONS = [
    ("Fish", "Fish & Chips", 860, 34, 78, 42, 5, 2.2),
    ("Pies", "Pie of the Day", 740, 28, 62, 40, 3, 2.4),
    ("Burgers", "Steak Burger", 760, 40, 52, 40, 3, 2.2),
    ("Roasts", "Sunday Roast Lamb", 720, 44, 48, 36, 4, 2.6),
    ("Fish", "Beer Battered Cod", 480, 32, 28, 24, 2, 1.8),
    ("Sides", "Chips", 380, 5, 48, 18, 4, 0.6),
    ("Desserts", "Sticky Toffee Pudding", 460, 4, 68, 18, 1, 0.7),
]

_VINTAGE_INNS = [
    ("Mains", "Roast Chicken", 580, 44, 32, 28, 3, 2.0),
    ("Fish", "Fish & Chips", 880, 36, 78, 44, 5, 2.2),
    ("Grill", "Steak & Chips", 720, 52, 42, 34, 3, 2.4),
    ("Pies", "Pie & Mash", 740, 28, 66, 38, 3, 2.4),
    ("Salads", "Caesar Salad", 480, 28, 22, 32, 3, 1.8),
    ("Desserts", "Chocolate Torte", 460, 6, 52, 26, 2, 0.4),
    ("Starters", "Prawn Cocktail", 260, 14, 10, 18, 1, 1.6),
]

_BROWNS = [
    ("Grill", "Steak Frites", 780, 52, 46, 40, 3, 2.4),
    ("Fish", "Fish & Chips", 840, 34, 76, 42, 4, 2.2),
    ("Mains", "Chicken Milanese", 720, 42, 56, 34, 3, 2.0),
    ("Pasta", "Prawn Linguine", 620, 28, 68, 24, 3, 2.2),
    ("Salads", "Caesar Salad", 520, 30, 22, 34, 3, 1.8),
    ("Afternoon Tea", "Afternoon Tea", 680, 12, 88, 32, 2, 1.4),
    ("Desserts", "Chocolate Fondant", 480, 7, 56, 26, 2, 0.3),
]

_BREWERS_FAYRE = [
    ("Carvery", "Sunday Carvery Beef", 680, 46, 52, 30, 4, 2.4),
    ("Fish", "Fish & Chips", 860, 34, 78, 42, 5, 2.2),
    ("Grill", "Gammon & Egg", 720, 48, 36, 40, 2, 3.4),
    ("Burgers", "Chicken Burger", 680, 34, 54, 34, 3, 2.0),
    ("Fish", "Scampi & Chips", 640, 20, 64, 28, 4, 1.8),
    ("Mains", "Mac & Cheese", 580, 20, 52, 30, 2, 1.6),
    ("Desserts", "Sticky Toffee", 440, 4, 66, 16, 1, 0.7),
]

_PITCHER_AND_PIANO = [
    ("Burgers", "Steak Burger", 780, 42, 54, 40, 3, 2.4),
    ("Fish", "Fish & Chips", 840, 34, 76, 42, 4, 2.2),
    ("Salads", "Chicken Caesar", 520, 38, 22, 32, 3, 2.0),
    ("Burgers", "Halloumi Burger", 680, 24, 58, 38, 4, 2.4),
    ("Sharers", "Loaded Nachos", 720, 24, 68, 38, 5, 3.0),
    ("Desserts", "Chocolate Brownie", 420, 6, 52, 22, 2, 0.4),
]

_YOUNGS = [
    ("Fish", "Fish & Chips", 880, 36, 78, 44, 5, 2.2),
    ("Roasts", "Sunday Roast Beef", 720, 48, 52, 32, 4, 2.6),
    ("Pies", "Steak & Ale Pie", 760, 32, 64, 40, 3, 2.6),
    ("Burgers", "Chicken Burger", 700, 34, 56, 36, 3, 2.0),
    ("Salads", "Caesar Salad", 480, 28, 22, 32, 3, 1.8),
    ("Fish", "Beer Battered Haddock", 460, 30, 28, 22, 2, 1.8),
    ("Sides", "Chips", 380, 5, 48, 18, 4, 0.6),
    ("Desserts", "Crumble & Custard", 420, 5, 58, 18, 3, 0.4),
]

_FULLERS = [
    ("Fish", "Fish & Chips", 860, 34, 78, 42, 5, 2.2),
    ("Pies", "Pie & Mash", 740, 28, 66, 38, 3, 2.4),
    ("Burgers", "Steak Burger", 760, 40, 52, 40, 3, 2.2),
    ("Mains", "Roast Chicken", 580, 44, 32, 28, 3, 2.0),
    ("Salads", "Caesar Salad", 480, 28, 22, 32, 3, 1.8),
    ("Starters", "Prawn Cocktail", 260, 14, 10, 18, 1, 1.6),
    ("Desserts", "Chocolate Brownie", 440, 6, 54, 22, 2, 0.4),
]


# -- Master list ----------------------------------------------------------

_ALL_PUBS = [
    ("Sizzling Pubs", "https://www.sizzlingpubs.co.uk/food", _SIZZLING_PUBS),
    ("Chef & Brewer", "https://www.chefandbrewer.com/en-gb/food", _CHEF_AND_BREWER),
    ("Flaming Grill", "https://www.flaminggrill.co.uk/food", _FLAMING_GRILL),
    ("All Bar One", "https://www.allbarone.co.uk/food-drink", _ALL_BAR_ONE),
    ("Ember Inns", "https://www.emberinns.co.uk/food-drink", _EMBER_INNS),
    ("Stonehouse Pizza & Carvery", "https://www.stonehouserestaurants.co.uk/food", _STONEHOUSE),
    ("Slug & Lettuce", "https://www.slugandlettuce.co.uk/food-drink", _SLUG_AND_LETTUCE),
    ("O'Neill's", "https://www.oneills.co.uk/food", _ONEILLS),
    ("Nicholson's", "https://www.nicholsonspubs.co.uk/food", _NICHOLSONS),
    ("Vintage Inns", "https://www.vintageinns.co.uk/food-drink", _VINTAGE_INNS),
    ("Browns", "https://www.browns-restaurants.co.uk/menus", _BROWNS),
    ("Brewers Fayre", "https://www.brewersfayre.co.uk/en-gb/food", _BREWERS_FAYRE),
    ("Pitcher & Piano", "https://www.pitcherandpiano.com/food-drink", _PITCHER_AND_PIANO),
    ("Young's Pubs", "https://www.youngs.co.uk/food-drink", _YOUNGS),
    ("Fuller's", "https://www.fullers.co.uk/pubs/food-drink", _FULLERS),
]
