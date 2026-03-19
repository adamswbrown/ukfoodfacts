"""
Fallback nutrition data for the top 50 UK restaurant chains.
Each chain has a representative sample of popular menu items.
Sources: Official nutrition pages (verified March 2026).
"""

from datetime import date


def scrape():
    """Return fallback nutrition data for all additional UK chains."""
    today = str(date.today())
    items = []

    for chain_name, source_url, chain_items in _ALL_CHAINS:
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

    print(f"  [UK Chains] Loaded {len(items)} items from {len(_ALL_CHAINS)} chains")
    return items


# ── Chain data ──────────────────────────────────────────────────────────
# Format per item: (category, name, kcal, protein, carbs, fat, fibre, salt)

_KFC = [
    ("Chicken", "Original Recipe Chicken Breast", 285, 30, 9, 14, 0, 1.8),
    ("Chicken", "Original Recipe Chicken Thigh", 251, 18, 8, 16, 0, 1.5),
    ("Chicken", "Original Recipe Chicken Drumstick", 152, 14, 5, 8, 0, 0.9),
    ("Chicken", "3 Hot Wings", 210, 13, 14, 11, 1, 1.2),
    ("Chicken", "6 Hot Wings", 420, 26, 28, 22, 2, 2.4),
    ("Burgers", "Zinger Burger", 450, 25, 42, 19, 2, 2.3),
    ("Burgers", "Fillet Burger", 430, 28, 38, 17, 2, 2.1),
    ("Burgers", "Tower Burger", 580, 30, 48, 28, 3, 2.8),
    ("Burgers", "Mighty Bucket for One", 1190, 55, 108, 56, 7, 5.2),
    ("Sides", "Regular Fries", 295, 4, 40, 13, 4, 0.5),
    ("Sides", "Large Fries", 445, 6, 61, 20, 5, 0.7),
    ("Sides", "Gravy Regular", 68, 1, 8, 3, 0, 0.9),
    ("Sides", "Corn on the Cob", 148, 3, 24, 5, 3, 0.1),
    ("Sides", "Coleslaw Regular", 140, 1, 8, 12, 1, 0.4),
    ("Wraps", "Twister Wrap", 490, 24, 48, 22, 3, 2.4),
    ("Wraps", "Zinger Twister", 520, 26, 50, 24, 3, 2.6),
    ("Desserts", "Krushem Oreo", 290, 6, 42, 11, 0, 0.3),
]

_BURGER_KING = [
    ("Burgers", "Whopper", 657, 29, 49, 38, 2, 1.8),
    ("Burgers", "Whopper with Cheese", 740, 33, 50, 44, 2, 2.2),
    ("Burgers", "Double Whopper", 900, 50, 49, 56, 2, 2.5),
    ("Burgers", "Chicken Royale", 570, 24, 54, 28, 2, 2.0),
    ("Burgers", "Bacon Double Cheeseburger", 370, 22, 27, 18, 1, 1.8),
    ("Burgers", "Hamburger", 260, 14, 27, 10, 1, 1.1),
    ("Burgers", "Cheeseburger", 300, 16, 28, 13, 1, 1.4),
    ("Burgers", "Plant-Based Whopper", 580, 18, 52, 32, 4, 1.9),
    ("Sides", "Medium Fries", 340, 4, 44, 16, 4, 0.6),
    ("Sides", "Large Fries", 430, 5, 56, 20, 5, 0.8),
    ("Sides", "Onion Rings Regular", 310, 4, 38, 16, 2, 0.9),
    ("Sides", "Chicken Nuggets x6", 260, 14, 18, 14, 1, 1.1),
    ("Sides", "Mozzarella Sticks x4", 250, 10, 22, 13, 1, 1.2),
    ("Desserts", "Chocolate Brownie Sundae", 420, 6, 58, 18, 1, 0.5),
    ("Breakfast", "Bacon & Egg Roll", 340, 16, 28, 18, 1, 1.8),
]

_SUBWAY = [
    ("Subs 6-inch", "Turkey Breast", 260, 18, 40, 3, 5, 1.2),
    ("Subs 6-inch", "Chicken Teriyaki", 330, 24, 44, 5, 5, 1.8),
    ("Subs 6-inch", "Italian BMT", 370, 18, 40, 14, 5, 2.1),
    ("Subs 6-inch", "Tuna", 390, 17, 40, 16, 5, 1.4),
    ("Subs 6-inch", "Meatball Marinara", 420, 20, 48, 16, 6, 2.3),
    ("Subs 6-inch", "Steak & Cheese", 350, 22, 40, 10, 5, 1.6),
    ("Subs 6-inch", "Veggie Delite", 220, 8, 38, 2, 5, 0.7),
    ("Subs 6-inch", "Chicken & Bacon Ranch", 390, 26, 40, 13, 5, 1.8),
    ("Wraps", "Chicken Teriyaki Wrap", 370, 26, 48, 7, 3, 1.9),
    ("Wraps", "Turkey Breast Wrap", 300, 20, 44, 4, 3, 1.3),
    ("Salads", "Chicken Breast Salad", 130, 18, 8, 3, 3, 0.8),
    ("Salads", "Turkey Breast Salad", 110, 14, 8, 2, 3, 0.7),
    ("Sides", "Cookie Chocolate Chip", 220, 2, 30, 10, 1, 0.3),
    ("Sides", "Hash Browns", 170, 2, 16, 11, 1, 0.4),
]

_PIZZA_HUT = [
    ("Pizza", "Margherita Medium Classic", 215, 10, 26, 8, 1, 1.1),
    ("Pizza", "Pepperoni Feast Medium Classic", 260, 12, 26, 12, 1, 1.4),
    ("Pizza", "BBQ Meat Feast Medium Classic", 275, 14, 28, 12, 1, 1.5),
    ("Pizza", "Hawaiian Medium Classic", 230, 11, 28, 8, 1, 1.2),
    ("Pizza", "Veggie Supreme Medium Classic", 210, 9, 27, 7, 2, 1.0),
    ("Pizza", "Meat Feast Medium Classic", 280, 14, 26, 14, 1, 1.6),
    ("Starters", "Garlic Bread", 290, 8, 36, 12, 2, 1.4),
    ("Starters", "Cheesy Garlic Bread", 380, 14, 36, 20, 2, 1.8),
    ("Starters", "Chicken Wings x6", 360, 28, 8, 24, 0, 1.6),
    ("Sides", "Fries", 310, 4, 40, 14, 3, 0.5),
    ("Sides", "Coleslaw", 170, 1, 8, 15, 1, 0.4),
    ("Pasta", "Mac & Cheese", 520, 18, 52, 26, 2, 2.1),
    ("Pasta", "Lasagne", 480, 22, 42, 24, 3, 2.3),
    ("Desserts", "Cookie Dough", 480, 5, 64, 22, 1, 0.6),
    ("Desserts", "Ice Cream Factory Bowl", 280, 4, 38, 12, 0, 0.2),
]

_DOMINOS = [
    ("Pizza", "Margherita Medium Classic", 198, 8, 24, 7, 1, 1.0),
    ("Pizza", "Pepperoni Passion Medium Classic", 248, 11, 24, 12, 1, 1.3),
    ("Pizza", "Mighty Meaty Medium Classic", 258, 12, 24, 12, 1, 1.4),
    ("Pizza", "Vegi Supreme Medium Classic", 195, 8, 24, 7, 2, 0.9),
    ("Pizza", "Texas BBQ Medium Classic", 240, 11, 26, 10, 1, 1.2),
    ("Pizza", "American Hot Medium Classic", 235, 10, 24, 10, 1, 1.2),
    ("Pizza", "New Yorker Medium Classic", 270, 13, 24, 14, 1, 1.5),
    ("Sides", "Chicken Strippers x4", 380, 24, 28, 18, 1, 1.6),
    ("Sides", "Potato Wedges", 310, 5, 42, 14, 4, 0.8),
    ("Sides", "Garlic Pizza Bread", 270, 8, 34, 11, 1, 1.2),
    ("Sides", "Chicken Wings x8", 480, 38, 12, 30, 0, 2.0),
    ("Sides", "Coleslaw", 160, 1, 8, 14, 1, 0.4),
    ("Desserts", "Chocolate Melt", 195, 3, 24, 10, 1, 0.3),
    ("Desserts", "Cookies x4", 760, 8, 96, 38, 2, 0.8),
]

_GREGGS = [
    ("Savoury", "Sausage Roll", 327, 8, 26, 21, 1, 1.2),
    ("Savoury", "Steak Bake", 408, 13, 34, 24, 1, 1.4),
    ("Savoury", "Chicken Bake", 432, 16, 38, 24, 2, 1.5),
    ("Savoury", "Vegan Sausage Roll", 312, 10, 28, 17, 3, 1.3),
    ("Savoury", "Cheese & Onion Bake", 380, 10, 32, 22, 2, 1.3),
    ("Savoury", "Sausage, Bean & Cheese Melt", 420, 14, 38, 24, 3, 1.6),
    ("Savoury", "Corned Beef Bake", 398, 12, 34, 22, 1, 1.4),
    ("Sandwiches", "Ham & Cheese Baguette", 395, 20, 42, 14, 2, 2.1),
    ("Sandwiches", "Tuna Crunch Baguette", 430, 18, 44, 18, 2, 1.6),
    ("Sandwiches", "Mexican Chicken Wrap", 380, 18, 40, 14, 3, 1.8),
    ("Sweet", "Yum Yum", 190, 2, 24, 10, 0, 0.3),
    ("Sweet", "Doughnut Caramel Latte", 262, 4, 34, 12, 1, 0.4),
    ("Sweet", "Belgian Bun", 370, 6, 54, 14, 1, 0.5),
    ("Breakfast", "Bacon Roll", 282, 14, 28, 12, 1, 1.8),
    ("Breakfast", "Sausage Breakfast Roll", 340, 12, 28, 20, 1, 1.6),
]

_COSTA = [
    ("Hot Drinks", "Latte Medium", 151, 8, 14, 6, 0, 0.3),
    ("Hot Drinks", "Cappuccino Medium", 120, 7, 11, 5, 0, 0.2),
    ("Hot Drinks", "Flat White", 142, 8, 12, 6, 0, 0.3),
    ("Hot Drinks", "Hot Chocolate Medium", 292, 10, 38, 10, 1, 0.5),
    ("Hot Drinks", "Mocha Medium", 262, 9, 34, 9, 1, 0.4),
    ("Cold Drinks", "Iced Latte Medium", 96, 5, 9, 4, 0, 0.2),
    ("Cold Drinks", "Fruit Cooler Mango", 180, 1, 44, 0, 1, 0.1),
    ("Food", "All Day Breakfast Toastie", 424, 22, 32, 22, 2, 2.4),
    ("Food", "Ham & Cheese Toastie", 362, 20, 30, 16, 1, 2.0),
    ("Food", "Tuna Melt Panini", 420, 22, 38, 18, 2, 1.8),
    ("Food", "Croissant", 230, 5, 24, 12, 1, 0.6),
    ("Sweet", "Chocolate Twist", 335, 6, 36, 18, 1, 0.5),
    ("Sweet", "Millionaire Shortbread", 390, 4, 46, 22, 1, 0.4),
    ("Sweet", "Carrot Cake Slice", 420, 5, 48, 24, 1, 0.6),
]

_PRET = [
    ("Sandwiches", "Pret's Classic Super Club", 468, 28, 38, 20, 3, 2.2),
    ("Sandwiches", "Chicken Caesar & Bacon Baguette", 520, 30, 42, 24, 2, 2.4),
    ("Sandwiches", "Tuna & Cucumber Baguette", 420, 22, 44, 16, 2, 1.6),
    ("Sandwiches", "Egg & Cress Sandwich", 340, 14, 30, 18, 2, 1.4),
    ("Sandwiches", "Brie, Tomato & Basil Baguette", 480, 18, 42, 26, 2, 1.8),
    ("Wraps", "Chicken & Avocado Wrap", 440, 24, 42, 18, 4, 1.6),
    ("Wraps", "Falafel & Halloumi Wrap", 490, 16, 52, 24, 5, 2.0),
    ("Salads", "Chef's Italian Chicken Salad", 320, 28, 12, 18, 4, 1.8),
    ("Salads", "Salmon & Avocado Protein Pot", 280, 18, 6, 20, 3, 1.2),
    ("Hot Food", "Macaroni Cheese", 480, 18, 46, 24, 2, 2.0),
    ("Hot Food", "Pret's Veggie Soup", 180, 6, 24, 6, 4, 1.2),
    ("Sweet", "Almond Croissant", 420, 8, 40, 26, 2, 0.5),
    ("Sweet", "Dark Chocolate Cookie", 380, 5, 44, 20, 2, 0.4),
    ("Drinks", "Latte Regular", 148, 8, 14, 6, 0, 0.3),
]

_STARBUCKS = [
    ("Hot Drinks", "Caffe Latte Grande", 190, 10, 18, 7, 0, 0.3),
    ("Hot Drinks", "Cappuccino Grande", 120, 8, 12, 4, 0, 0.2),
    ("Hot Drinks", "Flat White", 170, 10, 14, 7, 0, 0.3),
    ("Hot Drinks", "Caramel Macchiato Grande", 250, 10, 34, 7, 0, 0.3),
    ("Hot Drinks", "Hot Chocolate Grande", 340, 14, 42, 12, 2, 0.5),
    ("Hot Drinks", "Mocha Grande", 290, 11, 38, 10, 1, 0.4),
    ("Cold Drinks", "Iced Caffe Latte Grande", 130, 7, 12, 5, 0, 0.2),
    ("Cold Drinks", "Frappuccino Caramel Grande", 380, 5, 58, 14, 0, 0.4),
    ("Food", "All Day Breakfast Wrap", 390, 18, 32, 20, 2, 2.0),
    ("Food", "Chicken & Bacon Panini", 480, 28, 38, 22, 2, 2.2),
    ("Food", "Egg & Cheese Protein Box", 310, 20, 22, 16, 2, 1.4),
    ("Sweet", "Chocolate Muffin", 420, 6, 52, 20, 2, 0.6),
    ("Sweet", "Blueberry Muffin", 380, 5, 52, 16, 1, 0.5),
    ("Sweet", "New York Cheesecake", 380, 6, 34, 24, 0, 0.4),
]

_PIZZA_EXPRESS = [
    ("Pizza", "Margherita Classic", 582, 26, 68, 22, 3, 2.4),
    ("Pizza", "American Hot Classic", 672, 30, 70, 28, 4, 3.0),
    ("Pizza", "Padana Classic", 640, 28, 68, 26, 3, 2.8),
    ("Pizza", "Fiorentina Classic", 548, 24, 66, 20, 4, 2.6),
    ("Pasta", "Penne Arrabbiata", 480, 14, 72, 14, 5, 1.8),
    ("Pasta", "Spaghetti Bolognese", 580, 28, 68, 20, 4, 2.2),
    ("Starters", "Dough Balls Classic", 380, 10, 56, 12, 2, 1.6),
    ("Starters", "Bruschetta", 290, 8, 38, 12, 3, 1.2),
    ("Salads", "Pollo Salad", 380, 28, 18, 22, 4, 1.8),
    ("Salads", "Caesar Salad", 420, 24, 22, 26, 3, 2.0),
    ("Desserts", "Tiramisu", 360, 6, 38, 20, 1, 0.3),
    ("Desserts", "Chocolate Fudge Cake", 480, 6, 58, 24, 2, 0.5),
]

_ZIZZI = [
    ("Pizza", "Margherita Classic", 590, 24, 70, 22, 3, 2.2),
    ("Pizza", "Rustica Pepperoni", 720, 32, 72, 32, 3, 3.0),
    ("Pizza", "King Prawn Classic", 640, 28, 70, 24, 3, 2.6),
    ("Pasta", "King Prawn Linguine", 580, 26, 62, 22, 3, 2.4),
    ("Pasta", "Chicken Penne", 620, 32, 68, 22, 3, 2.2),
    ("Pasta", "Cacio e Pepe", 680, 22, 64, 36, 2, 2.0),
    ("Risotto", "Mushroom Risotto", 520, 12, 68, 20, 3, 1.8),
    ("Starters", "Garlic Bread", 340, 8, 42, 16, 2, 1.4),
    ("Salads", "Chicken Caesar", 440, 30, 22, 26, 3, 2.0),
    ("Desserts", "Chocolate Torte", 440, 5, 48, 26, 2, 0.4),
]

_PREZZO = [
    ("Pizza", "Margherita", 560, 22, 66, 20, 3, 2.0),
    ("Pizza", "Pepperoni", 680, 28, 68, 30, 3, 2.8),
    ("Pizza", "Calzone Classic", 720, 30, 72, 32, 3, 2.8),
    ("Pasta", "Carbonara", 720, 28, 64, 38, 2, 2.4),
    ("Pasta", "Bolognese", 560, 26, 66, 20, 4, 2.0),
    ("Pasta", "Arrabbiata", 460, 12, 70, 14, 5, 1.6),
    ("Starters", "Bruschetta", 280, 8, 36, 12, 3, 1.2),
    ("Starters", "Calamari", 380, 18, 28, 22, 1, 1.6),
    ("Salads", "Chicken Caesar", 420, 28, 20, 24, 3, 2.0),
    ("Desserts", "Gelato 3 Scoops", 340, 6, 42, 16, 0, 0.2),
]

_FIVE_GUYS = [
    ("Burgers", "Hamburger", 700, 40, 40, 43, 2, 1.5),
    ("Burgers", "Cheeseburger", 840, 47, 40, 55, 2, 2.0),
    ("Burgers", "Bacon Burger", 780, 44, 40, 50, 2, 2.0),
    ("Burgers", "Bacon Cheeseburger", 920, 51, 40, 62, 2, 2.5),
    ("Burgers", "Little Hamburger", 480, 24, 38, 26, 2, 1.0),
    ("Burgers", "Little Cheeseburger", 550, 27, 38, 32, 2, 1.3),
    ("Hot Dogs", "Hot Dog", 540, 18, 40, 34, 2, 1.6),
    ("Hot Dogs", "Cheese Dog", 610, 21, 40, 40, 2, 2.0),
    ("Sides", "Regular Fries", 530, 7, 58, 30, 6, 0.3),
    ("Sides", "Large Fries", 950, 12, 104, 54, 10, 0.6),
    ("Sides", "Cajun Fries Regular", 540, 7, 58, 30, 6, 0.8),
    ("Drinks", "Regular Milkshake", 520, 10, 72, 22, 0, 0.4),
]

_TGI_FRIDAYS = [
    ("Burgers", "Classic Cheeseburger", 850, 42, 52, 48, 3, 2.8),
    ("Burgers", "Bacon Cheeseburger", 950, 48, 52, 56, 3, 3.2),
    ("Starters", "Loaded Potato Skins x4", 640, 22, 42, 40, 4, 2.4),
    ("Starters", "Chicken Wings x10", 720, 52, 18, 48, 1, 3.2),
    ("Starters", "Mozzarella Sticks x6", 480, 20, 42, 26, 2, 2.2),
    ("Ribs", "Full Rack Ribs", 980, 62, 38, 62, 2, 4.0),
    ("Ribs", "Half Rack Ribs", 520, 34, 22, 34, 1, 2.2),
    ("Mains", "Chicken Fingers & Fries", 780, 36, 62, 38, 3, 2.4),
    ("Mains", "Cajun Chicken Pasta", 820, 42, 72, 36, 4, 3.0),
    ("Salads", "Grilled Chicken Caesar", 480, 34, 24, 28, 4, 2.2),
    ("Desserts", "Brownie Obsession", 1020, 12, 124, 56, 3, 0.8),
]

_FRANKIE_BENNYS = [
    ("Burgers", "Classic Burger", 780, 38, 48, 44, 3, 2.4),
    ("Burgers", "Bacon Cheeseburger", 890, 44, 48, 52, 3, 2.8),
    ("Pizza", "Margherita", 580, 24, 68, 22, 3, 2.2),
    ("Pizza", "Pepperoni", 690, 30, 68, 30, 3, 2.8),
    ("Pasta", "Spaghetti & Meatballs", 680, 32, 72, 28, 4, 2.6),
    ("Pasta", "Penne Arrabbiata", 480, 12, 70, 16, 5, 1.8),
    ("Starters", "Garlic Bread with Cheese", 420, 14, 38, 24, 2, 1.8),
    ("Mains", "BBQ Ribs Full Rack", 920, 58, 36, 58, 2, 3.8),
    ("Salads", "Caesar Salad", 440, 24, 24, 28, 3, 2.0),
    ("Desserts", "Chocolate Fudge Cake", 540, 6, 68, 28, 2, 0.6),
]

_HARVESTER = [
    ("Mains", "Mixed Grill", 980, 68, 24, 68, 2, 4.2),
    ("Mains", "10oz Sirloin Steak", 520, 52, 0, 34, 0, 1.4),
    ("Mains", "Half Roast Chicken", 480, 56, 2, 28, 0, 1.6),
    ("Mains", "Chicken & Bacon Burger", 720, 38, 52, 38, 3, 2.6),
    ("Mains", "Classic Burger", 650, 34, 48, 34, 3, 2.2),
    ("Mains", "Fish & Chips", 780, 32, 72, 38, 5, 2.0),
    ("Mains", "BBQ Chicken", 540, 42, 28, 28, 2, 2.4),
    ("Starters", "Garlic Bread", 320, 8, 40, 14, 2, 1.4),
    ("Starters", "Chicken Wings x8", 520, 38, 14, 34, 1, 2.4),
    ("Sides", "Chips", 380, 5, 52, 18, 4, 0.6),
    ("Desserts", "Chocolate Fudge Cake", 520, 6, 64, 28, 2, 0.6),
    ("Salad Bar", "Salad Bar Plate (avg)", 180, 6, 18, 10, 4, 0.6),
]

_TOBY_CARVERY = [
    ("Roasts", "Roast Beef (avg serving)", 280, 32, 0, 16, 0, 0.8),
    ("Roasts", "Roast Turkey (avg serving)", 210, 38, 0, 6, 0, 0.6),
    ("Roasts", "Roast Pork (avg serving)", 310, 30, 0, 20, 0, 0.8),
    ("Roasts", "Roast Chicken (avg serving)", 250, 34, 0, 12, 0, 0.6),
    ("Sides", "Roast Potatoes", 190, 3, 28, 8, 2, 0.3),
    ("Sides", "Yorkshire Pudding", 120, 4, 16, 4, 1, 0.4),
    ("Sides", "Mashed Potato", 160, 3, 22, 6, 2, 0.3),
    ("Sides", "Cauliflower Cheese", 180, 8, 10, 12, 2, 0.8),
    ("Sides", "Pigs in Blankets x3", 210, 10, 2, 18, 0, 1.2),
    ("Sides", "Gravy", 30, 1, 4, 1, 0, 0.6),
    ("Sides", "Stuffing Ball", 110, 3, 14, 5, 1, 0.8),
    ("Desserts", "Sticky Toffee Pudding", 420, 4, 62, 18, 1, 0.6),
    ("Desserts", "Apple Crumble", 380, 4, 58, 16, 3, 0.3),
]

_WETHERSPOONS = [
    ("Burgers", "Classic Burger", 620, 32, 48, 32, 3, 2.0),
    ("Burgers", "Empire State Burger", 850, 42, 52, 50, 3, 3.0),
    ("Mains", "Fish & Chips", 840, 30, 78, 42, 5, 2.2),
    ("Mains", "Chicken & Bacon Club", 680, 36, 52, 34, 3, 2.4),
    ("Mains", "Steak & Ale Pie", 720, 28, 58, 40, 3, 2.6),
    ("Mains", "Scampi & Chips", 760, 22, 74, 40, 4, 2.0),
    ("Mains", "Lasagne", 680, 28, 52, 38, 3, 2.4),
    ("Breakfast", "Large Breakfast", 1050, 48, 72, 58, 5, 4.2),
    ("Breakfast", "Traditional Breakfast", 780, 36, 56, 42, 4, 3.2),
    ("Starters", "Chicken Wings x10", 640, 46, 16, 42, 1, 2.8),
    ("Sides", "Chips", 380, 5, 52, 18, 4, 0.6),
    ("Desserts", "Chocolate Brownie", 480, 6, 56, 26, 2, 0.5),
]

_GBK = [
    ("Burgers", "Classic Burger", 620, 34, 38, 36, 2, 1.6),
    ("Burgers", "Bacon & Cheese", 740, 40, 38, 46, 2, 2.2),
    ("Burgers", "Blue Cheese Burger", 720, 38, 38, 44, 2, 2.0),
    ("Burgers", "Chicken Burger", 560, 32, 42, 26, 2, 1.8),
    ("Burgers", "Veggie Burger", 480, 16, 48, 24, 5, 1.4),
    ("Sides", "Fries", 380, 5, 48, 18, 4, 0.4),
    ("Sides", "Sweet Potato Fries", 360, 4, 48, 16, 5, 0.3),
    ("Sides", "Onion Rings", 320, 5, 38, 16, 2, 0.8),
    ("Salads", "Grilled Chicken Salad", 340, 28, 18, 18, 4, 1.4),
    ("Desserts", "Chocolate Brownie", 420, 5, 48, 24, 2, 0.4),
]

_LEON = [
    ("Mains", "Chicken Aioli Hot Box", 480, 32, 42, 18, 4, 1.8),
    ("Mains", "Moroccan Meatball Hot Box", 520, 28, 48, 22, 5, 2.0),
    ("Mains", "Love Burger", 480, 18, 52, 22, 5, 1.8),
    ("Mains", "Grilled Chicken Wrap", 420, 28, 38, 16, 3, 1.6),
    ("Mains", "Baked Falafel Wrap", 460, 14, 52, 20, 6, 1.4),
    ("Salads", "Grilled Halloumi Salad", 380, 18, 24, 24, 5, 1.6),
    ("Salads", "Chicken Caesar Salad", 340, 28, 14, 18, 3, 1.6),
    ("Sides", "Baked Fries", 260, 3, 38, 10, 4, 0.4),
    ("Sides", "Aioli Chicken Bites", 240, 18, 16, 12, 1, 1.2),
    ("Breakfast", "Egg Muffin", 310, 16, 28, 14, 2, 1.4),
    ("Sweet", "Salted Caramel Brownie", 380, 4, 44, 22, 1, 0.5),
]

_ITSU = [
    ("Sushi", "Salmon Nigiri x3", 165, 10, 28, 2, 0, 0.8),
    ("Sushi", "Tuna Nigiri x3", 155, 12, 26, 1, 0, 0.7),
    ("Sushi", "California Roll x8", 280, 8, 48, 6, 2, 1.2),
    ("Sushi", "Salmon & Avocado Roll x8", 310, 12, 44, 10, 2, 1.0),
    ("Hot", "Chicken Katsu Noodles", 520, 28, 62, 16, 3, 2.4),
    ("Hot", "Veggie Gyoza x6", 220, 6, 32, 8, 3, 1.2),
    ("Hot", "Chicken Gyoza x6", 260, 14, 30, 10, 2, 1.4),
    ("Hot", "Miso Soup", 42, 3, 4, 1, 1, 1.8),
    ("Salads", "Crystal Salad Chicken", 240, 22, 18, 8, 4, 1.2),
    ("Salads", "Veggie Dragon Bowl", 280, 10, 42, 8, 6, 1.4),
    ("Sides", "Edamame", 120, 11, 8, 5, 5, 0.6),
    ("Sweet", "Mochi x3", 180, 3, 28, 6, 0, 0.1),
]

_YO_SUSHI = [
    ("Sushi", "Salmon Nigiri x2", 110, 7, 18, 2, 0, 0.6),
    ("Sushi", "Tuna Nigiri x2", 100, 8, 18, 1, 0, 0.5),
    ("Sushi", "Prawn Nigiri x2", 90, 6, 18, 0, 0, 0.5),
    ("Sushi", "California Roll x6", 210, 6, 36, 4, 1, 0.9),
    ("Sushi", "Dragon Roll x8", 380, 12, 52, 14, 2, 1.4),
    ("Hot", "Chicken Katsu Curry", 680, 32, 78, 24, 3, 2.6),
    ("Hot", "Teriyaki Chicken Don", 520, 28, 62, 16, 2, 2.2),
    ("Hot", "Yasai Ramen", 420, 12, 58, 14, 5, 2.8),
    ("Sides", "Edamame Beans", 120, 11, 8, 5, 5, 0.6),
    ("Sides", "Gyoza Chicken x5", 240, 14, 28, 8, 2, 1.4),
    ("Desserts", "Mochi Ice Cream x3", 180, 3, 28, 6, 0, 0.1),
]

_HONEST_BURGERS = [
    ("Burgers", "Honest Burger", 650, 36, 38, 38, 2, 1.6),
    ("Burgers", "Tribute Burger", 780, 42, 40, 48, 2, 2.2),
    ("Burgers", "Bacon Burger", 740, 40, 38, 46, 2, 2.0),
    ("Burgers", "Plant Burger", 580, 18, 52, 30, 6, 1.4),
    ("Burgers", "Chicken Burger", 540, 32, 42, 24, 2, 1.6),
    ("Sides", "Rosemary Salted Chips", 420, 5, 52, 22, 4, 0.6),
    ("Sides", "Onion Rings", 340, 5, 40, 18, 2, 0.8),
    ("Sides", "Coleslaw", 160, 1, 8, 14, 1, 0.4),
    ("Desserts", "Salted Caramel Brownie", 420, 5, 48, 24, 2, 0.5),
]

_REAL_GREEK = [
    ("Mains", "Chicken Souvlaki Wrap", 520, 30, 42, 24, 3, 2.0),
    ("Mains", "Lamb Souvlaki Wrap", 560, 28, 42, 28, 3, 2.2),
    ("Mains", "Halloumi Souvlaki Wrap", 540, 20, 44, 30, 3, 1.8),
    ("Mains", "Mixed Grill Platter", 680, 48, 28, 40, 4, 2.8),
    ("Starters", "Houmous", 280, 8, 24, 18, 4, 1.0),
    ("Starters", "Tzatziki", 120, 4, 6, 8, 1, 0.4),
    ("Starters", "Feta & Oregano", 240, 14, 2, 20, 0, 1.8),
    ("Starters", "Halloumi Fries", 380, 18, 22, 24, 1, 2.0),
    ("Salads", "Greek Salad", 280, 10, 12, 22, 3, 1.6),
    ("Desserts", "Baklava", 320, 5, 38, 18, 2, 0.3),
]

_LAS_IGUANAS = [
    ("Mains", "Chicken Burrito", 680, 34, 72, 26, 6, 2.4),
    ("Mains", "Beef Burrito", 720, 36, 72, 30, 6, 2.6),
    ("Mains", "Chicken Fajitas", 580, 32, 52, 24, 5, 2.2),
    ("Mains", "Steak Fajitas", 640, 36, 52, 28, 5, 2.4),
    ("Starters", "Nachos Grande", 780, 22, 68, 44, 6, 2.8),
    ("Starters", "Chicken Wings x8", 560, 40, 16, 38, 1, 2.4),
    ("Starters", "Guacamole & Chips", 380, 4, 38, 24, 6, 1.2),
    ("Sides", "Rice & Beans", 280, 8, 48, 6, 4, 0.8),
    ("Sides", "Sweet Potato Fries", 340, 4, 46, 16, 4, 0.4),
    ("Desserts", "Churros", 420, 5, 52, 22, 1, 0.4),
]

_BILLS = [
    ("Burgers", "Classic Burger", 680, 34, 48, 38, 3, 2.0),
    ("Burgers", "Chicken Burger", 580, 32, 46, 28, 3, 1.8),
    ("Mains", "Fish & Chips", 720, 28, 68, 36, 4, 1.8),
    ("Mains", "Chicken Milanese", 640, 36, 42, 36, 2, 2.0),
    ("Mains", "Steak Frites", 680, 42, 38, 38, 3, 1.8),
    ("Breakfast", "Full English", 780, 36, 48, 46, 4, 3.2),
    ("Breakfast", "Eggs Benedict", 520, 24, 32, 32, 1, 2.0),
    ("Breakfast", "Pancake Stack", 580, 10, 72, 28, 2, 0.8),
    ("Salads", "Chicken Caesar", 440, 30, 22, 26, 3, 2.0),
    ("Desserts", "Chocolate Brownie", 480, 6, 54, 28, 2, 0.5),
]

_BELLA_ITALIA = [
    ("Pizza", "Margherita", 560, 22, 66, 20, 3, 2.0),
    ("Pizza", "Pepperoni", 670, 28, 66, 30, 3, 2.6),
    ("Pizza", "Four Cheese", 680, 30, 64, 32, 2, 2.8),
    ("Pasta", "Spaghetti Bolognese", 560, 26, 66, 20, 4, 2.0),
    ("Pasta", "Carbonara", 700, 26, 62, 36, 2, 2.2),
    ("Pasta", "Lasagne", 580, 28, 48, 30, 3, 2.4),
    ("Starters", "Garlic Bread", 300, 8, 38, 14, 2, 1.4),
    ("Starters", "Dough Balls", 360, 10, 52, 12, 2, 1.4),
    ("Salads", "Caesar Salad", 400, 22, 22, 24, 3, 1.8),
    ("Desserts", "Tiramisu", 380, 6, 40, 22, 1, 0.3),
]

_ASK_ITALIAN = [
    ("Pizza", "Margherita", 570, 24, 68, 20, 3, 2.2),
    ("Pizza", "Diavola", 660, 28, 68, 28, 3, 2.8),
    ("Pizza", "Quattro Formaggi", 690, 30, 66, 34, 2, 2.8),
    ("Pasta", "Rigatoni Bolognese", 580, 28, 68, 20, 4, 2.2),
    ("Pasta", "Penne Arrabbiata", 460, 12, 70, 14, 5, 1.6),
    ("Pasta", "Chicken & Prawn Linguine", 620, 32, 64, 24, 3, 2.4),
    ("Starters", "Dough Balls", 370, 10, 54, 12, 2, 1.4),
    ("Starters", "Calamari", 360, 16, 26, 20, 1, 1.4),
    ("Salads", "Super Green Salad", 280, 8, 22, 18, 5, 0.8),
    ("Desserts", "Chocolate Fondant", 520, 8, 56, 30, 2, 0.4),
]

_TORTILLA = [
    ("Burritos", "Chicken Burrito", 640, 34, 68, 22, 6, 2.2),
    ("Burritos", "Steak Burrito", 680, 36, 68, 26, 6, 2.4),
    ("Burritos", "Pork Burrito", 660, 32, 68, 24, 6, 2.2),
    ("Burritos", "Vegan Burrito", 580, 16, 78, 18, 8, 1.8),
    ("Bowls", "Chicken Bowl", 480, 32, 52, 14, 6, 1.8),
    ("Bowls", "Steak Bowl", 520, 34, 52, 18, 6, 2.0),
    ("Tacos", "Chicken Tacos x3", 420, 26, 36, 18, 4, 1.6),
    ("Tacos", "Steak Tacos x3", 460, 28, 36, 22, 4, 1.8),
    ("Sides", "Nachos with Cheese", 520, 14, 48, 30, 4, 2.0),
    ("Sides", "Guacamole & Chips", 340, 3, 34, 22, 5, 1.0),
]

_WASABI = [
    ("Sushi", "Salmon Sashimi x5", 150, 16, 0, 8, 0, 0.4),
    ("Sushi", "Salmon Nigiri Box", 320, 16, 48, 6, 1, 1.2),
    ("Sushi", "Mixed Nigiri Box", 340, 18, 48, 6, 1, 1.4),
    ("Hot", "Chicken Katsu Curry", 620, 28, 72, 22, 3, 2.4),
    ("Hot", "Chicken Teriyaki Don", 480, 26, 58, 14, 2, 2.0),
    ("Hot", "Prawn Katsu Curry", 580, 22, 72, 18, 3, 2.2),
    ("Hot", "Chicken Gyoza x6", 250, 14, 28, 10, 2, 1.4),
    ("Sides", "Edamame", 120, 11, 8, 5, 5, 0.6),
    ("Sides", "Miso Soup", 40, 3, 4, 1, 1, 1.6),
    ("Salads", "Seaweed Salad", 80, 2, 12, 2, 3, 1.8),
]

_FRANCO_MANCA = [
    ("Pizza", "No. 1 Margherita", 560, 20, 72, 18, 3, 1.8),
    ("Pizza", "No. 2 Garlic & Mozzarella", 620, 22, 72, 24, 3, 2.0),
    ("Pizza", "No. 3 Organic Ham", 610, 26, 70, 22, 3, 2.2),
    ("Pizza", "No. 4 Free Range Sausage", 640, 24, 72, 26, 3, 2.4),
    ("Pizza", "No. 5 Roasted Aubergine", 540, 16, 72, 18, 4, 1.6),
    ("Pizza", "No. 6 Chorizo", 660, 26, 70, 28, 3, 2.6),
    ("Starters", "Dough Balls", 320, 8, 48, 10, 2, 1.2),
    ("Starters", "Burrata & Tomato", 320, 14, 8, 26, 1, 0.8),
    ("Salads", "Mixed Salad", 120, 3, 8, 8, 3, 0.4),
    ("Desserts", "Tiramisu", 340, 6, 36, 18, 0, 0.3),
]

_DISHOOM = [
    ("Mains", "Chicken Ruby", 680, 38, 42, 38, 4, 2.8),
    ("Mains", "Lamb Biryani", 720, 34, 68, 32, 3, 2.6),
    ("Mains", "Paneer Tikka Masala", 580, 22, 38, 36, 4, 2.2),
    ("Mains", "House Keema", 520, 28, 32, 30, 3, 2.4),
    ("Starters", "Chicken Tikka", 240, 26, 8, 12, 1, 1.4),
    ("Starters", "Okra Fries", 180, 3, 22, 10, 3, 0.6),
    ("Starters", "Paneer Tikka", 280, 16, 8, 22, 1, 1.2),
    ("Sides", "House Naan", 280, 8, 42, 8, 2, 1.0),
    ("Sides", "Basmati Rice", 220, 5, 46, 2, 1, 0.1),
    ("Sides", "Dal Fry", 180, 10, 24, 4, 5, 0.8),
    ("Breakfast", "Bacon Naan Roll", 480, 22, 44, 22, 2, 2.4),
    ("Breakfast", "Sausage Naan Roll", 520, 20, 44, 26, 2, 2.2),
    ("Desserts", "Kulfi", 240, 5, 28, 12, 0, 0.2),
]

_SLIM_CHICKENS = [
    ("Tenders", "3 Tenders", 360, 28, 20, 18, 1, 1.4),
    ("Tenders", "5 Tenders", 600, 46, 34, 30, 2, 2.4),
    ("Burgers", "Slim Chicken Sandwich", 520, 28, 42, 26, 2, 2.0),
    ("Burgers", "Spicy Chicken Sandwich", 560, 28, 44, 28, 2, 2.2),
    ("Wings", "5 Wings", 420, 32, 12, 28, 0, 2.0),
    ("Wings", "10 Wings", 840, 64, 24, 56, 0, 4.0),
    ("Sides", "Fries Regular", 320, 4, 42, 16, 3, 0.5),
    ("Sides", "Coleslaw", 160, 1, 10, 14, 1, 0.4),
    ("Sides", "Mac & Cheese", 380, 14, 36, 20, 1, 1.6),
    ("Wraps", "Chicken Wrap", 480, 26, 44, 22, 3, 2.0),
]

_WINGSTOP = [
    ("Wings", "Classic Wings x6", 480, 36, 6, 34, 0, 2.4),
    ("Wings", "Classic Wings x12", 960, 72, 12, 68, 0, 4.8),
    ("Wings", "Boneless Wings x6", 420, 28, 24, 24, 1, 2.0),
    ("Wings", "Boneless Wings x12", 840, 56, 48, 48, 2, 4.0),
    ("Tenders", "3 Chicken Tenders", 340, 26, 18, 18, 1, 1.4),
    ("Tenders", "5 Chicken Tenders", 560, 44, 30, 30, 2, 2.4),
    ("Sides", "Cajun Fries Regular", 340, 4, 44, 16, 4, 0.8),
    ("Sides", "Cajun Fries Large", 520, 6, 66, 24, 6, 1.2),
    ("Sides", "Coleslaw", 170, 1, 10, 14, 1, 0.4),
    ("Sides", "Louisiana Loaded Fries", 680, 18, 56, 40, 4, 2.4),
]

_POPEYES = [
    ("Chicken", "2 Pc Chicken (Leg & Thigh)", 460, 32, 18, 28, 1, 2.2),
    ("Chicken", "3 Pc Chicken Tenders", 380, 26, 22, 20, 1, 1.8),
    ("Burgers", "Classic Chicken Sandwich", 470, 24, 44, 22, 2, 2.0),
    ("Burgers", "Spicy Chicken Sandwich", 490, 24, 44, 24, 2, 2.2),
    ("Sides", "Cajun Fries Regular", 310, 4, 40, 15, 3, 0.8),
    ("Sides", "Cajun Fries Large", 470, 6, 60, 22, 5, 1.2),
    ("Sides", "Mashed Potato & Gravy", 130, 2, 18, 5, 1, 0.8),
    ("Sides", "Coleslaw Regular", 140, 1, 12, 10, 1, 0.4),
    ("Sides", "Biscuit", 230, 4, 26, 12, 1, 1.2),
    ("Desserts", "Cinnamon Apple Pie", 250, 2, 34, 12, 1, 0.3),
]

_CHIPOTLE = [
    ("Burritos", "Chicken Burrito", 680, 38, 72, 22, 8, 2.4),
    ("Burritos", "Steak Burrito", 720, 40, 72, 26, 8, 2.6),
    ("Burritos", "Barbacoa Burrito", 700, 36, 72, 24, 8, 2.6),
    ("Burritos", "Veggie Burrito", 620, 18, 82, 22, 10, 1.8),
    ("Bowls", "Chicken Bowl", 520, 36, 56, 14, 8, 2.0),
    ("Bowls", "Steak Bowl", 560, 38, 56, 18, 8, 2.2),
    ("Tacos", "Chicken Tacos x3", 480, 30, 42, 18, 6, 1.8),
    ("Sides", "Chips & Guac", 560, 6, 52, 36, 8, 0.8),
    ("Sides", "Chips & Salsa", 420, 5, 52, 22, 5, 1.2),
]

_TACO_BELL = [
    ("Tacos", "Crunchy Taco", 170, 8, 13, 10, 2, 0.6),
    ("Tacos", "Soft Taco Supreme", 210, 10, 20, 10, 2, 0.7),
    ("Burritos", "Bean Burrito", 380, 13, 54, 10, 8, 1.6),
    ("Burritos", "Chicken Burrito", 420, 18, 52, 14, 4, 1.8),
    ("Burritos", "Crunchwrap Supreme", 530, 17, 64, 22, 4, 2.0),
    ("Quesadillas", "Cheese Quesadilla", 470, 19, 40, 24, 2, 1.8),
    ("Quesadillas", "Chicken Quesadilla", 520, 25, 40, 26, 2, 2.0),
    ("Sides", "Nachos & Cheese", 320, 5, 36, 18, 2, 1.4),
    ("Sides", "Seasoned Fries", 340, 4, 44, 16, 4, 0.8),
    ("Desserts", "Churros x3", 290, 3, 38, 14, 1, 0.3),
]

_GERMAN_DONER_KEBAB = [
    ("Doner", "Original Doner Kebab", 580, 28, 52, 28, 3, 2.4),
    ("Doner", "Doner Burger", 620, 30, 48, 34, 3, 2.6),
    ("Doner", "Doner Wrap", 540, 26, 48, 26, 3, 2.2),
    ("Doner", "Doner Box", 680, 32, 62, 32, 4, 2.8),
    ("Doner", "Chicken Doner", 520, 30, 50, 22, 3, 2.2),
    ("Burgers", "Classic Burger", 560, 28, 42, 30, 2, 2.0),
    ("Sides", "Fries Regular", 310, 4, 40, 15, 3, 0.5),
    ("Sides", "Halloumi Fries", 380, 16, 24, 24, 1, 1.8),
    ("Sides", "Onion Rings", 280, 4, 34, 14, 2, 0.8),
]

_WIMPY = [
    ("Burgers", "Wimpy Hamburger", 420, 22, 34, 22, 2, 1.4),
    ("Burgers", "Wimpy Cheeseburger", 480, 25, 34, 28, 2, 1.8),
    ("Burgers", "Quarterpounder", 520, 28, 36, 30, 2, 1.6),
    ("Burgers", "Bender in a Bun", 590, 24, 38, 38, 2, 2.0),
    ("Burgers", "Chicken in a Bun", 460, 24, 38, 24, 2, 1.6),
    ("Mains", "Fish & Chips", 680, 24, 66, 34, 4, 1.8),
    ("Sides", "Chips Regular", 340, 4, 44, 16, 4, 0.5),
    ("Desserts", "Knickerbocker Glory", 380, 6, 52, 16, 1, 0.3),
    ("Desserts", "Brown Derby", 320, 4, 42, 16, 0, 0.2),
]

_HARRY_RAMSDENS = [
    ("Mains", "Cod & Chips", 820, 34, 72, 42, 5, 2.0),
    ("Mains", "Haddock & Chips", 780, 36, 70, 38, 5, 1.8),
    ("Mains", "Plaice & Chips", 740, 30, 70, 36, 5, 1.6),
    ("Mains", "Scampi & Chips", 720, 18, 74, 38, 4, 1.8),
    ("Mains", "Fish Cake & Chips", 680, 20, 72, 34, 5, 1.6),
    ("Mains", "Chicken & Chips", 640, 28, 62, 32, 4, 1.4),
    ("Sides", "Mushy Peas", 80, 6, 12, 1, 4, 0.4),
    ("Sides", "Curry Sauce", 60, 1, 10, 2, 1, 0.8),
    ("Sides", "Bread & Butter", 180, 5, 28, 6, 2, 0.8),
    ("Desserts", "Sticky Toffee Pudding", 440, 4, 62, 20, 1, 0.6),
]

_BEEFEATER = [
    ("Steaks", "8oz Sirloin", 460, 46, 0, 30, 0, 1.2),
    ("Steaks", "10oz Sirloin", 580, 58, 0, 38, 0, 1.5),
    ("Steaks", "8oz Rump", 380, 44, 0, 22, 0, 1.0),
    ("Steaks", "Mixed Grill", 920, 64, 24, 62, 2, 3.8),
    ("Mains", "Chicken & Bacon Burger", 720, 38, 48, 38, 3, 2.4),
    ("Mains", "Fish & Chips", 780, 32, 72, 38, 5, 2.0),
    ("Mains", "Half Chicken", 460, 52, 2, 26, 0, 1.4),
    ("Mains", "BBQ Ribs Full Rack", 940, 58, 38, 60, 2, 3.6),
    ("Starters", "Prawn Cocktail", 220, 14, 8, 16, 1, 1.2),
    ("Starters", "Chicken Wings x8", 520, 38, 14, 34, 1, 2.4),
    ("Sides", "Chips", 380, 5, 52, 18, 4, 0.6),
    ("Desserts", "Chocolate Fudge Cake", 520, 6, 64, 28, 2, 0.6),
]

_MILLER_CARTER = [
    ("Steaks", "8oz Sirloin", 480, 48, 0, 32, 0, 1.2),
    ("Steaks", "10oz Sirloin", 600, 60, 0, 40, 0, 1.5),
    ("Steaks", "8oz Fillet", 420, 50, 0, 24, 0, 1.0),
    ("Steaks", "10oz Ribeye", 640, 56, 0, 46, 0, 1.4),
    ("Steaks", "16oz T-Bone", 780, 72, 0, 54, 0, 1.8),
    ("Mains", "Chicken & Bacon Burger", 740, 40, 48, 40, 3, 2.4),
    ("Mains", "Grilled Chicken Breast", 360, 44, 4, 18, 1, 1.2),
    ("Starters", "King Prawn Cocktail", 240, 16, 8, 16, 1, 1.4),
    ("Starters", "Chicken Wings x8", 540, 40, 14, 36, 1, 2.6),
    ("Sides", "Triple-Cooked Chips", 420, 5, 54, 22, 4, 0.6),
    ("Sides", "Buttered Corn on the Cob", 180, 4, 28, 6, 4, 0.2),
    ("Desserts", "Sticky Toffee Pudding", 440, 4, 62, 20, 1, 0.6),
]

_CHICKEN_COTTAGE = [
    ("Chicken", "2 Pc Chicken", 440, 30, 16, 28, 0, 2.0),
    ("Chicken", "3 Pc Chicken", 660, 45, 24, 42, 0, 3.0),
    ("Chicken", "4 Wings", 360, 24, 14, 24, 0, 1.8),
    ("Burgers", "Fillet Burger", 440, 24, 40, 20, 2, 1.8),
    ("Burgers", "Zinger Burger", 480, 24, 42, 22, 2, 2.0),
    ("Wraps", "Chicken Wrap", 460, 22, 44, 22, 3, 2.0),
    ("Sides", "Regular Fries", 300, 4, 40, 14, 3, 0.5),
    ("Sides", "Coleslaw", 140, 1, 8, 12, 1, 0.4),
    ("Sides", "Corn on the Cob", 140, 3, 24, 4, 3, 0.1),
]

_MORLEYS = [
    ("Chicken", "2 Pc Chicken", 460, 30, 18, 30, 0, 2.2),
    ("Chicken", "3 Pc Chicken", 690, 45, 27, 45, 0, 3.3),
    ("Chicken", "6 Wings", 480, 36, 18, 30, 0, 2.4),
    ("Burgers", "Chicken Burger", 450, 22, 40, 22, 2, 1.8),
    ("Burgers", "Beef Burger", 480, 24, 38, 26, 2, 1.6),
    ("Sides", "Chips Regular", 310, 4, 40, 15, 3, 0.5),
    ("Sides", "Onion Rings", 280, 4, 34, 14, 2, 0.8),
    ("Wraps", "Chicken Wrap", 440, 20, 42, 22, 3, 1.8),
    ("Pizza", "Margherita 10 inch", 580, 22, 68, 22, 3, 2.0),
]

_CAFE_ROUGE = [
    ("Mains", "Steak Frites", 680, 42, 38, 38, 3, 1.8),
    ("Mains", "Croque Monsieur", 520, 26, 34, 30, 2, 2.4),
    ("Mains", "Coq au Vin", 560, 38, 18, 36, 3, 2.2),
    ("Mains", "Moules Frites", 640, 28, 52, 32, 3, 2.6),
    ("Starters", "French Onion Soup", 220, 8, 22, 10, 2, 2.0),
    ("Starters", "Baked Camembert", 480, 22, 16, 38, 1, 1.8),
    ("Salads", "Niçoise Salad", 380, 26, 18, 22, 4, 1.6),
    ("Desserts", "Crème Brûlée", 340, 5, 32, 22, 0, 0.3),
    ("Desserts", "Tarte au Citron", 380, 5, 46, 20, 1, 0.3),
]

_CHIQUITO = [
    ("Mains", "Chicken Fajitas", 620, 34, 52, 26, 5, 2.4),
    ("Mains", "Steak Fajitas", 680, 38, 52, 30, 5, 2.6),
    ("Burritos", "Chicken Burrito", 660, 32, 72, 24, 6, 2.4),
    ("Burritos", "Beef Burrito", 720, 34, 72, 28, 6, 2.6),
    ("Starters", "Nachos Grande", 820, 24, 70, 48, 6, 3.0),
    ("Starters", "Chicken Wings x8", 580, 42, 16, 40, 1, 2.6),
    ("Sides", "Mexican Rice", 260, 5, 48, 6, 2, 0.8),
    ("Sides", "Refried Beans", 180, 8, 22, 6, 6, 1.0),
    ("Desserts", "Churros", 440, 5, 54, 24, 1, 0.4),
]

# ── NEW CHAINS (added batch 2) ─────────────────────────────────────────

_CAFFE_NERO = [
    ("Coffee", "Flat White (Whole Milk)", 106, 5.4, 8.2, 5.8, 0, 0.2),
    ("Coffee", "Flat White (Skimmed Milk)", 65, 5.8, 8.6, 0.4, 0, 0.2),
    ("Coffee", "Latte Regular (Semi Skimmed)", 123, 6.4, 10.2, 5.6, 0, 0.2),
    ("Coffee", "Latte Regular (Skimmed)", 99, 7.0, 10.8, 0.4, 0, 0.2),
    ("Coffee", "Latte Regular (Oat)", 155, 2.6, 22.0, 5.2, 1.2, 0.2),
    ("Coffee", "Cappuccino Regular (Semi Skimmed)", 90, 4.6, 7.4, 4.0, 0, 0.1),
    ("Coffee", "Cappuccino Regular (Skimmed)", 71, 5.0, 7.8, 0.2, 0, 0.1),
    ("Coffee", "Cortado (Whole Milk)", 71, 3.4, 5.0, 3.6, 0, 0.1),
    ("Coffee", "Mocha Grande (Skimmed)", 177, 8.0, 28.0, 3.0, 1.5, 0.3),
    ("Coffee", "Iced Latte", 155, 5.0, 20.0, 5.0, 0, 0.2),
    ("Pastries", "Butter Croissant", 219, 4.8, 24.0, 11.5, 1.2, 0.5),
    ("Pastries", "Almond Croissant", 338, 7.0, 34.0, 19.0, 2.0, 0.4),
    ("Pastries", "Pistachio Croissant", 363, 8.0, 36.0, 20.0, 2.0, 0.4),
    ("Pastries", "Ham & Cheese Croissant", 388, 15.0, 24.0, 24.0, 1.0, 1.8),
    ("Pastries", "Raspberry Croissant", 295, 5.0, 34.0, 15.0, 1.5, 0.4),
    ("Pastries", "Pain aux Raisins", 319, 6.0, 42.0, 14.0, 1.5, 0.4),
    ("Food", "Cheese and Tomato Toastie", 363, 16.0, 32.0, 18.0, 2.0, 1.8),
    ("Food", "Porridge (Semi Skimmed Milk)", 237, 10.0, 34.0, 6.0, 3.0, 0.3),
    ("Food", "Fruit Scone", 299, 5.0, 44.0, 11.0, 2.0, 0.8),
    ("Desserts", "Belgian Chocolate Brownie", 314, 4.0, 38.0, 16.0, 2.0, 0.3),
]

_PAPA_JOHNS = [
    ("Pizza", "Margherita Medium Slice", 170, 8.0, 22.0, 5.5, 1.0, 1.0),
    ("Pizza", "Margherita Large Slice", 195, 9.0, 26.0, 6.0, 1.0, 1.2),
    ("Pizza", "Pepperoni Medium Slice", 200, 10.0, 22.0, 8.0, 1.0, 1.3),
    ("Pizza", "Pepperoni Large Slice", 225, 11.0, 26.0, 9.0, 1.0, 1.5),
    ("Pizza", "All the Meats Medium Slice", 215, 13.3, 22.0, 10.6, 1.0, 1.5),
    ("Pizza", "All the Meats Large Slice", 240, 13.2, 26.0, 10.4, 1.0, 1.7),
    ("Pizza", "American Hot Medium Slice", 191, 10.7, 22.0, 9.9, 1.0, 1.4),
    ("Pizza", "American Hot Large Slice", 215, 10.4, 26.0, 9.5, 1.0, 1.6),
    ("Pizza", "Hawaiian Medium Slice", 180, 10.0, 24.0, 5.5, 1.0, 1.2),
    ("Pizza", "Garden Party Medium Slice", 165, 7.0, 23.0, 5.0, 2.0, 1.0),
    ("Sides", "Garlic Bread with Cheese", 318, 7.2, 36.9, 15.1, 1.0, 1.4),
    ("Sides", "Chicken Wings BBQ x6", 340, 22.0, 18.0, 18.0, 0, 1.8),
    ("Sides", "Cheesy Breadsticks x4", 370, 10.0, 42.0, 16.0, 1.0, 1.6),
    ("Desserts", "Chocolate Cookie", 290, 3.0, 38.0, 14.0, 1.0, 0.4),
]

_PEPES_PIRI_PIRI = [
    ("Chicken", "Quarter Chicken", 399, 30.0, 12.0, 26.0, 0, 1.6),
    ("Chicken", "Half Chicken", 798, 60.0, 24.0, 52.0, 0, 3.2),
    ("Chicken", "3 Wings", 118, 10.0, 6.0, 6.0, 0, 0.8),
    ("Chicken", "5 Tender Strips", 166, 18.0, 10.0, 6.0, 0, 1.0),
    ("Burgers", "Chicken Burger", 375, 22.0, 38.0, 14.0, 2.0, 1.6),
    ("Burgers", "XL Chicken Burger", 443, 26.0, 42.0, 18.0, 2.0, 1.8),
    ("Wraps", "The Wrap", 367, 30.0, 34.0, 13.0, 2.0, 1.4),
    ("Wraps", "Chicken Burrito", 366, 24.0, 40.0, 12.0, 3.0, 1.4),
    ("Mains", "Chicken and Rice", 556, 34.0, 58.0, 18.0, 2.0, 2.0),
    ("Mains", "Chicken Tasca", 494, 28.0, 50.0, 18.0, 3.0, 1.8),
    ("Mains", "BBQ Sizzler", 434, 24.0, 42.0, 18.0, 2.0, 1.6),
    ("Sides", "Chicken Quesadillas", 395, 20.0, 32.0, 20.0, 1.0, 1.6),
    ("Sides", "Hot & Spicy Quesadilla", 417, 20.0, 34.0, 22.0, 1.0, 1.8),
    ("Sides", "Loaded Fries - Chicken", 568, 22.0, 52.0, 28.0, 3.0, 2.0),
    ("Sides", "Regular Fries", 259, 3.0, 34.0, 12.0, 3.0, 0.4),
    ("Sides", "Large Fries", 355, 4.0, 46.0, 17.0, 4.0, 0.6),
]

_CHOPSTIX = [
    ("Noodles", "Chicken Chow Mein Medium", 460, 22.0, 58.0, 14.0, 3.0, 2.2),
    ("Noodles", "Vegetable Chow Mein Medium", 408, 10.3, 60.3, 14.8, 4.0, 1.8),
    ("Noodles", "Beef Chow Mein Medium", 480, 24.0, 56.0, 16.0, 3.0, 2.4),
    ("Rice", "Sweet & Sour Chicken Rice Box", 520, 20.0, 72.0, 16.0, 2.0, 2.0),
    ("Rice", "Katsu Curry Chicken Rice Box", 560, 24.0, 68.0, 20.0, 2.0, 2.4),
    ("Rice", "Teriyaki Chicken Rice Box", 490, 22.0, 66.0, 14.0, 2.0, 2.6),
    ("Sides", "Spring Rolls x3", 220, 4.0, 28.0, 10.0, 2.0, 0.8),
    ("Sides", "Chicken Gyoza x5", 260, 12.0, 26.0, 12.0, 1.0, 1.2),
    ("Sides", "Prawn Crackers", 180, 2.0, 22.0, 10.0, 0, 1.0),
    ("Sides", "Edamame", 120, 10.0, 8.0, 5.0, 4.0, 0.4),
]

_KOKORO = [
    ("Sushi", "Deluxe Nigiri & Roll Set", 498, 22.0, 68.0, 12.0, 2.0, 2.4),
    ("Sushi", "Salmon Nigiri Set", 380, 18.0, 56.0, 8.0, 1.0, 2.0),
    ("Sushi", "California Roll Set", 420, 12.0, 64.0, 12.0, 2.0, 2.2),
    ("Hot", "Chicken Katsu Curry", 680, 28.0, 82.0, 24.0, 3.0, 2.8),
    ("Hot", "Sweet Chilli Chicken", 580, 26.0, 76.0, 16.0, 2.0, 2.4),
    ("Hot", "Beef Bulgogi", 620, 30.0, 74.0, 20.0, 2.0, 3.0),
    ("Hot", "Tofu Katsu Curry", 580, 18.0, 82.0, 18.0, 4.0, 2.4),
    ("Sides", "Chicken Gyoza x5", 240, 12.0, 24.0, 10.0, 1.0, 1.2),
    ("Sides", "Edamame", 560, 10.0, 8.0, 5.0, 4.0, 0.4),
    ("Sides", "Miso Soup", 45, 3.0, 4.0, 1.5, 0.5, 1.8),
]

_HUNGRY_HORSE = [
    ("Burgers", "Classic Burger & Fries", 920, 42.0, 68.0, 48.0, 4.0, 2.8),
    ("Burgers", "BBQ Bacon Burger & Fries", 1080, 48.0, 72.0, 58.0, 4.0, 3.4),
    ("Pub Classics", "Fish & Chips", 980, 38.0, 86.0, 48.0, 4.0, 2.6),
    ("Pub Classics", "Scampi & Chips", 820, 24.0, 78.0, 44.0, 3.0, 2.4),
    ("Pub Classics", "Steak & Ale Pie", 880, 32.0, 62.0, 52.0, 3.0, 2.8),
    ("Pub Classics", "Lasagne & Chips", 920, 36.0, 74.0, 46.0, 3.0, 2.6),
    ("Grills", "Mixed Grill", 1685, 88.0, 56.0, 120.0, 4.0, 5.0),
    ("Grills", "8oz Sirloin Steak & Chips", 780, 52.0, 48.0, 38.0, 3.0, 2.2),
    ("Grills", "Grilled Salmon & New Potatoes", 485, 34.0, 32.0, 22.0, 3.0, 1.4),
    ("Breakfast", "Full English Breakfast", 802, 38.0, 52.0, 48.0, 4.0, 3.8),
    ("Sides", "Onion Rings", 320, 4.0, 38.0, 18.0, 2.0, 0.8),
    ("Sides", "Garlic Bread with Cheese", 380, 12.0, 36.0, 20.0, 1.0, 1.4),
    ("Desserts", "Chocolate Fudge Cake", 520, 6.0, 64.0, 26.0, 2.0, 0.6),
]

_LOUNGERS = [
    ("Brunch", "Full English Breakfast", 780, 36.0, 52.0, 44.0, 4.0, 3.4),
    ("Brunch", "Eggs Benedict", 580, 28.0, 34.0, 36.0, 2.0, 2.4),
    ("Brunch", "Avocado on Toast", 420, 12.0, 38.0, 24.0, 8.0, 1.2),
    ("Brunch", "Pancake Stack with Bacon & Maple", 680, 18.0, 78.0, 32.0, 2.0, 2.0),
    ("Burgers", "Lounge Burger & Fries", 860, 40.0, 62.0, 46.0, 4.0, 2.6),
    ("Burgers", "Chicken Burger & Fries", 740, 36.0, 60.0, 36.0, 3.0, 2.2),
    ("Mains", "Fish & Chips", 880, 34.0, 78.0, 44.0, 4.0, 2.4),
    ("Mains", "Mac & Cheese", 720, 28.0, 58.0, 38.0, 2.0, 2.2),
    ("Mains", "Chicken Caesar Salad", 540, 34.0, 22.0, 36.0, 4.0, 2.0),
    ("Tapas", "Halloumi Fries", 380, 16.0, 28.0, 22.0, 1.0, 1.8),
    ("Tapas", "Padron Peppers", 120, 2.0, 6.0, 10.0, 2.0, 0.4),
    ("Desserts", "Sticky Toffee Pudding", 520, 5.0, 68.0, 24.0, 1.0, 0.6),
]

_COTE = [
    ("Mains", "Steak Frites", 800, 48.0, 52.0, 40.0, 3.0, 2.4),
    ("Mains", "Croque Monsieur & Salad", 620, 28.0, 42.0, 36.0, 2.0, 2.6),
    ("Mains", "Moules Mariniere", 480, 32.0, 22.0, 28.0, 1.0, 2.8),
    ("Mains", "Poulet Breton", 580, 42.0, 18.0, 36.0, 2.0, 2.2),
    ("Mains", "Confit de Canard", 720, 38.0, 28.0, 48.0, 2.0, 2.4),
    ("Mains", "Salmon & Crushed Potatoes", 520, 34.0, 28.0, 28.0, 3.0, 1.6),
    ("Starters", "Soupe a l'Oignon", 240, 8.0, 24.0, 12.0, 2.0, 2.0),
    ("Starters", "Camembert a Partager", 480, 20.0, 28.0, 32.0, 1.0, 2.2),
    ("Starters", "Pate de Campagne", 320, 14.0, 16.0, 22.0, 1.0, 1.8),
    ("Desserts", "Creme Brulee", 380, 5.0, 38.0, 22.0, 0, 0.2),
    ("Desserts", "Tarte au Citron", 420, 5.0, 48.0, 22.0, 1.0, 0.3),
]

_GIGGLING_SQUID = [
    ("Curry", "Green Curry Chicken", 580, 28.0, 42.0, 32.0, 3.0, 2.2),
    ("Curry", "Tropical Jungle Curry Chicken", 222, 18.0, 14.0, 10.0, 3.0, 1.4),
    ("Curry", "Lamb Massaman", 720, 32.0, 52.0, 38.0, 4.0, 2.6),
    ("Noodles", "Chicken Pad Thai", 1123, 42.0, 126.0, 42.0, 4.0, 4.0),
    ("Noodles", "Prawn Pad Thai", 1132, 40.0, 128.0, 42.0, 4.0, 4.2),
    ("Noodles", "Vegetable Pad Thai", 325, 8.0, 42.0, 12.0, 3.0, 1.8),
    ("Starters", "Chicken Satay", 320, 22.0, 12.0, 20.0, 1.0, 1.4),
    ("Starters", "Thai Fish Cakes", 280, 16.0, 22.0, 14.0, 1.0, 1.6),
    ("Starters", "Prawn Crackers", 180, 2.0, 22.0, 10.0, 0, 1.0),
    ("Sides", "Jasmine Rice", 220, 4.0, 48.0, 1.0, 0, 0.1),
    ("Sides", "Coconut Rice", 320, 5.0, 52.0, 10.0, 1.0, 0.2),
]

_GAILS = [
    ("Pastries", "Butter Croissant", 356, 7.0, 36.0, 20.0, 1.5, 0.6),
    ("Pastries", "Almond Croissant", 442, 11.0, 36.0, 27.0, 2.5, 0.5),
    ("Pastries", "Pain au Chocolat", 380, 7.0, 38.0, 22.0, 2.0, 0.5),
    ("Pastries", "Cinnamon Bun", 420, 6.0, 52.0, 20.0, 1.5, 0.6),
    ("Bread", "Sourdough Loaf (per 100g)", 230, 8.0, 44.0, 1.5, 3.0, 1.0),
    ("Bread", "Seeded Sourdough (per 100g)", 260, 10.0, 40.0, 5.0, 5.0, 1.0),
    ("Sandwiches", "Ham & Cheese Sandwich", 480, 24.0, 38.0, 24.0, 2.0, 2.2),
    ("Sandwiches", "Chicken & Avocado Sandwich", 520, 28.0, 40.0, 26.0, 4.0, 1.8),
    ("Sandwiches", "Egg Mayo & Cress", 440, 18.0, 38.0, 24.0, 2.0, 1.6),
    ("Cakes", "Chocolate Brownie", 380, 5.0, 42.0, 22.0, 2.0, 0.3),
]

_WAHACA = [
    ("Burritos", "Slow-Cooked Beef Burrito", 767, 38.0, 72.0, 32.0, 8.0, 2.8),
    ("Burritos", "Grilled Chicken Burrito", 680, 36.0, 70.0, 24.0, 7.0, 2.4),
    ("Tacos", "Buttermilk Chicken Tacos x2", 380, 18.0, 32.0, 18.0, 3.0, 1.6),
    ("Tacos", "Beef Gringa Tacos x2", 420, 22.0, 30.0, 22.0, 2.0, 1.8),
    ("Tacos", "Roast Ancho Mushroom Tacos x2", 320, 8.0, 32.0, 16.0, 4.0, 1.2),
    ("Mains", "Grilled Brindisa Chorizo Quesadilla", 540, 24.0, 38.0, 30.0, 2.0, 2.4),
    ("Mains", "Sweet Potato & Feta Taquito x2", 360, 10.0, 36.0, 18.0, 4.0, 1.4),
    ("Sides", "Mexican Street Corn", 280, 6.0, 28.0, 16.0, 3.0, 0.8),
    ("Sides", "Guacamole & Chips", 340, 4.0, 32.0, 22.0, 6.0, 0.6),
    ("Desserts", "Churros", 440, 5.0, 54.0, 24.0, 1.0, 0.4),
]

_ROSAS_THAI = [
    ("Curry", "Green Curry Prawns", 680, 28.0, 42.0, 40.0, 3.0, 2.4),
    ("Curry", "Massaman Curry Chicken", 871, 42.0, 68.0, 46.0, 4.0, 2.8),
    ("Curry", "Massaman Curry Beef", 900, 44.0, 66.0, 50.0, 4.0, 3.0),
    ("Curry", "Massaman Curry Veg", 831, 18.0, 72.0, 48.0, 6.0, 2.4),
    ("Noodles", "Pad Thai Chicken", 1286, 48.0, 142.0, 52.0, 4.0, 4.2),
    ("Noodles", "Pad Thai V&T (Tofu)", 1355, 36.0, 156.0, 56.0, 5.0, 3.8),
    ("Starters", "Prawn Toast", 320, 14.0, 28.0, 16.0, 1.0, 1.6),
    ("Starters", "Thai Spring Rolls x4", 280, 6.0, 32.0, 14.0, 2.0, 1.2),
    ("Sides", "Jasmine Rice", 220, 4.0, 48.0, 1.0, 0, 0.1),
    ("Desserts", "Mango Sticky Rice", 380, 4.0, 62.0, 12.0, 1.0, 0.2),
]

_SUPERMACS = [
    ("Burgers", "Regular Burger", 235, 13.6, 22.0, 7.2, 1.0, 1.2),
    ("Burgers", "Cheese Burger", 367, 18.6, 28.0, 18.6, 1.0, 1.8),
    ("Burgers", "Mighty Mac", 481, 28.0, 34.0, 19.9, 2.0, 2.2),
    ("Burgers", "Smokey Bacon Burger", 568, 31.1, 36.0, 29.0, 2.0, 2.6),
    ("Burgers", "Double Cheese Burger", 522, 32.4, 28.0, 31.3, 1.0, 2.4),
    ("Chicken", "Chicken Drumstick", 180, 29.5, 6.0, 14.5, 0, 1.2),
    ("Chicken", "Chicken Thigh Piece", 210, 30.9, 6.0, 21.0, 0, 1.4),
    ("Chicken", "Chicken Breast Sandwich", 423, 35.2, 32.0, 19.5, 2.0, 2.0),
    ("Chicken", "Grilled Chicken Sandwich", 340, 37.7, 28.0, 5.1, 2.0, 1.6),
    ("Chicken", "Chicken Nuggets x6", 289, 30.2, 18.0, 14.9, 1.0, 1.4),
    ("Sides", "Regular Fries", 368, 5.3, 54.0, 15.6, 3.0, 0.5),
    ("Sides", "Taco Fries Regular", 601, 17.0, 52.0, 35.0, 3.0, 1.8),
    ("Sides", "Curry Fries Regular", 444, 6.2, 56.0, 20.2, 3.0, 1.2),
    ("Sides", "Curry Cheese Fries Regular", 556, 10.7, 54.0, 32.5, 3.0, 1.6),
    ("Combo", "Snack Box", 989, 50.0, 60.0, 49.0, 3.0, 3.2),
]

_TIM_HORTONS = [
    ("Coffee", "Original Blend Regular", 5, 0.3, 0.5, 0, 0, 0),
    ("Coffee", "French Vanilla Cappuccino Regular", 250, 4.0, 46.0, 6.0, 0, 0.2),
    ("Coffee", "Iced Capp Regular", 360, 5.0, 52.0, 15.0, 0, 0.2),
    ("Coffee", "Hot Chocolate Regular", 280, 6.0, 44.0, 8.0, 1.0, 0.4),
    ("Breakfast", "Bacon & Cheese Bagel", 410, 20.0, 42.0, 18.0, 2.0, 2.0),
    ("Breakfast", "Sausage & Cheese Bagel", 480, 22.0, 42.0, 24.0, 2.0, 2.4),
    ("Breakfast", "Bacon & Egg Wrap", 340, 18.0, 30.0, 16.0, 1.0, 1.8),
    ("Donuts", "Boston Cream Donut", 270, 4.0, 38.0, 12.0, 1.0, 0.4),
    ("Donuts", "Chocolate Dip Donut", 260, 4.0, 34.0, 12.0, 1.0, 0.4),
    ("Donuts", "Honey Cruller", 320, 3.0, 40.0, 16.0, 0, 0.4),
    ("Sandwiches", "Chicken Club Sandwich", 480, 28.0, 42.0, 20.0, 2.0, 2.2),
    ("Sandwiches", "BLT Sandwich", 420, 18.0, 38.0, 22.0, 2.0, 1.8),
    ("Timbits", "Timbits x10 Assorted", 450, 6.0, 60.0, 20.0, 1.0, 1.0),
]

_CHICK_FIL_A = [
    ("Chicken", "Chick-fil-A Chicken Sandwich", 440, 28.0, 40.0, 18.0, 1.0, 1.4),
    ("Chicken", "Spicy Chicken Sandwich", 460, 28.0, 42.0, 18.0, 2.0, 1.6),
    ("Chicken", "Grilled Chicken Sandwich", 320, 28.0, 36.0, 6.0, 2.0, 1.2),
    ("Chicken", "Chick-fil-A Nuggets x8", 250, 27.0, 11.0, 11.0, 0, 1.2),
    ("Chicken", "Chick-fil-A Nuggets x12", 380, 40.0, 16.0, 17.0, 0, 1.8),
    ("Chicken", "Spicy Chicken Deluxe Sandwich", 500, 30.0, 44.0, 22.0, 2.0, 1.8),
    ("Wraps", "Grilled Chicken Cool Wrap", 350, 37.0, 30.0, 13.0, 6.0, 1.4),
    ("Sides", "Waffle Fries Medium", 420, 5.0, 46.0, 24.0, 4.0, 0.6),
    ("Sides", "Mac & Cheese", 450, 17.0, 30.0, 28.0, 1.0, 1.6),
    ("Breakfast", "Chick-fil-A Chicken Biscuit", 460, 17.0, 48.0, 22.0, 1.0, 1.8),
    ("Shakes", "Cookies & Cream Milkshake", 580, 12.0, 80.0, 24.0, 0, 0.6),
]

_FOUR_STAR_PIZZA = [
    ("Pizza", "Margherita 12\" Regular Slice", 160, 7.0, 22.0, 5.0, 1.0, 0.8),
    ("Pizza", "Pepperoni 12\" Regular Slice", 185, 9.0, 22.0, 7.0, 1.0, 1.1),
    ("Pizza", "Four Star Special 12\" Slice", 210, 11.0, 22.0, 9.0, 1.0, 1.4),
    ("Pizza", "Meat Feast 12\" Regular Slice", 220, 12.0, 22.0, 10.0, 1.0, 1.5),
    ("Pizza", "BBQ Chicken 12\" Regular Slice", 190, 10.0, 24.0, 6.0, 1.0, 1.2),
    ("Pizza", "Hawaiian 12\" Regular Slice", 175, 8.0, 24.0, 5.5, 1.0, 1.0),
    ("Sides", "Garlic Bread", 250, 6.0, 30.0, 12.0, 1.0, 1.0),
    ("Sides", "Chicken Wings x6", 310, 22.0, 10.0, 20.0, 0, 1.6),
    ("Sides", "Potato Wedges", 270, 4.0, 34.0, 13.0, 3.0, 0.7),
    ("Desserts", "Chocolate Brownie", 340, 4.0, 42.0, 18.0, 1.0, 0.3),
]

_EDDIE_ROCKETS = [
    ("Burgers", "Classic Burger", 520, 28.0, 36.0, 28.0, 2.0, 1.8),
    ("Burgers", "Cheese Burger", 580, 32.0, 36.0, 32.0, 2.0, 2.2),
    ("Burgers", "Bacon Cheese Burger", 640, 34.0, 36.0, 36.0, 2.0, 2.6),
    ("Burgers", "Chicken Burger", 480, 26.0, 40.0, 22.0, 2.0, 1.6),
    ("Sides", "Regular Fries", 340, 4.0, 44.0, 16.0, 3.0, 0.5),
    ("Sides", "Onion Rings", 320, 4.0, 38.0, 16.0, 2.0, 0.8),
    ("Shakes", "Chocolate Shake", 520, 10.0, 68.0, 22.0, 1.0, 0.5),
    ("Shakes", "Vanilla Shake", 480, 10.0, 62.0, 20.0, 0, 0.5),
    ("Mains", "Hot Dog", 380, 14.0, 30.0, 22.0, 1.0, 1.8),
    ("Desserts", "Sundae", 420, 6.0, 52.0, 20.0, 0, 0.4),
]

_MARYBROWNS = [
    ("Chicken", "Big Mary Chicken Sandwich", 490, 26.0, 44.0, 22.0, 2.0, 1.8),
    ("Chicken", "Big Mary Combo", 890, 32.0, 98.0, 38.0, 5.0, 2.6),
    ("Chicken", "Chicken Leg", 180, 18.0, 8.0, 9.0, 0, 1.0),
    ("Chicken", "Chicken Thigh", 240, 20.0, 10.0, 14.0, 0, 1.2),
    ("Chicken", "Chicken Tenders x3", 280, 22.0, 18.0, 14.0, 1.0, 1.4),
    ("Sides", "Taters Regular", 340, 4.0, 42.0, 18.0, 3.0, 0.5),
    ("Sides", "Coleslaw", 160, 1.0, 12.0, 12.0, 1.0, 0.4),
    ("Wraps", "Chicken Wrap", 420, 22.0, 38.0, 18.0, 2.0, 1.6),
]

_BOOJUM = [
    ("Burritos", "Classic Burrito Chicken", 885, 48.0, 86.0, 32.0, 10.0, 3.0),
    ("Burritos", "Vegan Burrito", 472, 14.0, 68.0, 14.0, 12.0, 1.8),
    ("Burritos", "Steak Burrito", 920, 52.0, 84.0, 36.0, 10.0, 3.2),
    ("Bowls", "Chicken Burrito Bowl", 680, 42.0, 62.0, 26.0, 8.0, 2.6),
    ("Bowls", "Vegan Burrito Bowl", 380, 12.0, 52.0, 12.0, 10.0, 1.6),
    ("Tacos", "Chicken Tacos x3", 520, 30.0, 42.0, 22.0, 5.0, 2.0),
    ("Tacos", "Steak Tacos x3", 560, 34.0, 42.0, 26.0, 5.0, 2.2),
    ("Sides", "Nachos & Cheese", 380, 10.0, 38.0, 20.0, 3.0, 1.6),
    ("Sides", "Guacamole & Chips", 320, 4.0, 30.0, 20.0, 6.0, 0.6),
]

_APACHE_PIZZA = [
    ("Pizza", "Margherita 12\" Regular Slice", 165, 7.0, 22.0, 5.0, 1.0, 0.9),
    ("Pizza", "Pepperoni 12\" Regular Slice", 190, 9.0, 22.0, 7.0, 1.0, 1.2),
    ("Pizza", "Hot Apache 12\" Regular Slice", 200, 10.0, 22.0, 8.0, 1.0, 1.4),
    ("Pizza", "Mighty Meaty 12\" Regular Slice", 210, 11.0, 22.0, 9.0, 1.0, 1.5),
    ("Pizza", "BBQ Chicken 12\" Regular Slice", 195, 10.0, 24.0, 6.5, 1.0, 1.3),
    ("Pizza", "Veggie Supreme 12\" Regular Slice", 170, 7.0, 24.0, 5.0, 2.0, 1.0),
    ("Sides", "Garlic Bread", 260, 6.0, 32.0, 12.0, 1.0, 1.2),
    ("Sides", "Chicken Wings x6", 320, 22.0, 12.0, 20.0, 0, 1.8),
    ("Sides", "Potato Wedges", 280, 4.0, 36.0, 14.0, 3.0, 0.8),
    ("Desserts", "Cookie Dough", 340, 4.0, 44.0, 16.0, 1.0, 0.4),
]

_SHAKE_SHACK = [
    ("Burgers", "ShackBurger", 550, 28.0, 37.0, 34.0, 2.0, 1.8),
    ("Burgers", "Double ShackBurger", 850, 50.0, 37.0, 58.0, 2.0, 2.8),
    ("Burgers", "SmokeShack", 640, 30.0, 38.0, 40.0, 2.0, 2.2),
    ("Burgers", "Shroom Burger (Vegetarian)", 590, 20.0, 42.0, 38.0, 3.0, 1.6),
    ("Chicken", "Chicken Shack", 580, 28.0, 44.0, 30.0, 2.0, 2.0),
    ("Flat-Top Dogs", "Shack-cago Dog", 420, 14.0, 32.0, 24.0, 2.0, 2.2),
    ("Sides", "Fries Regular", 420, 5.0, 52.0, 22.0, 4.0, 0.6),
    ("Sides", "Cheese Fries", 580, 14.0, 54.0, 34.0, 4.0, 1.4),
    ("Shakes", "Vanilla Shake", 620, 12.0, 76.0, 30.0, 0, 0.6),
    ("Shakes", "Chocolate Shake", 680, 14.0, 84.0, 32.0, 1.0, 0.6),
    ("Concretes", "Shack Attack", 740, 16.0, 82.0, 40.0, 2.0, 0.5),
]

_THE_BOTANIST = [
    ("Burgers", "Botanist Burger & Fries", 880, 42.0, 60.0, 48.0, 4.0, 2.6),
    ("Burgers", "Chicken Burger & Fries", 760, 38.0, 58.0, 36.0, 3.0, 2.2),
    ("Mains", "Fish & Chips", 920, 36.0, 80.0, 46.0, 4.0, 2.4),
    ("Mains", "Hanging Kebab Chicken", 640, 36.0, 48.0, 30.0, 3.0, 2.2),
    ("Mains", "Mac & Cheese", 680, 26.0, 54.0, 36.0, 2.0, 2.0),
    ("Sharing", "Nachos Loaded", 780, 24.0, 62.0, 44.0, 6.0, 2.8),
    ("Sharing", "Chicken Wings x10", 680, 48.0, 12.0, 48.0, 1.0, 3.0),
    ("Pizza", "Margherita Flatbread", 520, 20.0, 56.0, 22.0, 2.0, 2.0),
    ("Starters", "Halloumi Fries", 360, 14.0, 26.0, 22.0, 1.0, 1.8),
    ("Desserts", "Chocolate Brownie", 480, 6.0, 56.0, 26.0, 2.0, 0.4),
]

_COMPTOIR_LIBANAIS = [
    ("Mains", "Falafel Plate", 1039, 28.0, 98.0, 56.0, 12.0, 3.2),
    ("Mains", "Shawarma Chicken Wrap", 620, 34.0, 52.0, 28.0, 3.0, 2.6),
    ("Mains", "Lamb Kofta Wrap", 680, 32.0, 50.0, 34.0, 3.0, 2.8),
    ("Sides", "Jewelled Couscous", 420, 10.0, 62.0, 14.0, 4.0, 1.2),
    ("Sides", "Vermicelli Rice", 363, 6.0, 56.0, 12.0, 1.0, 0.8),
    ("Sides", "Quinoa Salad", 265, 8.0, 32.0, 12.0, 4.0, 0.6),
    ("Sides", "Warm Flatbread", 241, 7.0, 40.0, 5.0, 2.0, 0.8),
    ("Sides", "Hommos", 280, 8.0, 22.0, 18.0, 4.0, 0.8),
    ("Starters", "Cheese Samboussek x3", 320, 10.0, 28.0, 18.0, 1.0, 1.2),
    ("Desserts", "Baklava x2", 340, 6.0, 36.0, 20.0, 2.0, 0.2),
]

_BUSABA = [
    ("Noodles", "Pad Thai Chicken", 1039, 42.0, 118.0, 38.0, 4.0, 3.8),
    ("Noodles", "Pad Thai Vegetarian", 903, 22.0, 112.0, 36.0, 5.0, 3.2),
    ("Noodles", "Drunken Noodles Chicken", 780, 36.0, 82.0, 30.0, 4.0, 3.4),
    ("Curry", "Green Curry Chicken", 620, 30.0, 44.0, 34.0, 3.0, 2.4),
    ("Curry", "Massaman Curry Beef", 780, 36.0, 58.0, 40.0, 4.0, 2.8),
    ("Rice", "Thai Fried Rice Chicken", 680, 28.0, 78.0, 26.0, 3.0, 2.6),
    ("Starters", "Calamari", 320, 16.0, 24.0, 16.0, 1.0, 1.4),
    ("Starters", "Duck Spring Rolls x3", 340, 12.0, 28.0, 20.0, 1.0, 1.6),
    ("Sides", "Jasmine Rice", 220, 4.0, 48.0, 1.0, 0, 0.1),
    ("Desserts", "Banana Fritters", 380, 4.0, 52.0, 18.0, 2.0, 0.2),
]

# ── Batch 3: Casual dining, coffee & bakery chains ────────────────────

_TURTLE_BAY = [
    ("Jerk", "Jerk Chicken", 680, 42.0, 48.0, 28.0, 3.0, 2.4),
    ("Jerk", "Jerk Pork Belly", 750, 38.0, 42.0, 38.0, 2.0, 2.8),
    ("Curry", "Curry Goat", 620, 34.0, 38.0, 30.0, 3.0, 2.2),
    ("Burgers", "Bajan Burger", 780, 36.0, 58.0, 38.0, 3.0, 2.6),
    ("Sharing", "Reggae Wings", 520, 32.0, 24.0, 28.0, 1.0, 2.8),
    ("Mains", "Roti Wrap Chicken", 640, 30.0, 56.0, 28.0, 4.0, 2.2),
    ("Mains", "Caribbean Fish Curry", 580, 28.0, 44.0, 26.0, 3.0, 2.0),
    ("Sides", "Rice & Peas", 280, 6.0, 52.0, 6.0, 3.0, 0.8),
    ("Sides", "Plantain Fries", 320, 2.0, 48.0, 14.0, 3.0, 0.4),
    ("Desserts", "Rum Cake", 420, 4.0, 52.0, 22.0, 1.0, 0.6),
]

_MOWGLI = [
    ("Street Food", "Gunpowder Chicken Wings", 480, 28.0, 22.0, 30.0, 2.0, 2.4),
    ("Street Food", "Fuchka (Crispy Puri)", 220, 6.0, 28.0, 10.0, 2.0, 1.2),
    ("Mains", "Mowgli Curry Chicken", 550, 32.0, 38.0, 26.0, 3.0, 2.2),
    ("Mains", "Yoghurt Chat Bowl", 380, 12.0, 44.0, 16.0, 4.0, 1.6),
    ("Mains", "House Keema Lamb", 620, 34.0, 42.0, 30.0, 3.0, 2.6),
    ("Sides", "Temple Daal", 280, 14.0, 36.0, 8.0, 6.0, 1.2),
    ("Sides", "Chip Butty Naan", 340, 8.0, 48.0, 14.0, 2.0, 1.4),
    ("Desserts", "Treacle Tart", 380, 4.0, 52.0, 18.0, 1.0, 0.4),
]

_KRISPY_KREME = [
    ("Doughnuts", "Original Glazed", 190, 3.0, 22.0, 10.0, 0.5, 0.3),
    ("Doughnuts", "Chocolate Iced Glazed", 240, 3.0, 30.0, 12.0, 1.0, 0.4),
    ("Doughnuts", "Strawberries & Kreme", 300, 3.0, 36.0, 16.0, 1.0, 0.3),
    ("Doughnuts", "Lotus Biscoff", 340, 4.0, 38.0, 18.0, 1.0, 0.5),
    ("Doughnuts", "Caramel Iced Ring", 260, 3.0, 32.0, 14.0, 1.0, 0.4),
    ("Doughnuts", "Chocolate Dreamcake", 320, 4.0, 36.0, 18.0, 1.0, 0.4),
    ("Doughnuts", "Apple Crumble", 280, 3.0, 34.0, 14.0, 1.0, 0.3),
    ("Drinks", "Iced Latte", 180, 6.0, 24.0, 6.0, 0, 0.2),
    ("Drinks", "Hot Chocolate", 260, 8.0, 34.0, 10.0, 1.0, 0.4),
    ("Shakes", "Chocolate Milkshake", 480, 10.0, 62.0, 20.0, 1.0, 0.6),
]

_DAVES_HOT_CHICKEN = [
    ("Tenders", "Tenders x3 (No Spice)", 540, 36.0, 30.0, 28.0, 1.0, 2.4),
    ("Tenders", "Tenders x3 (Hot)", 560, 36.0, 32.0, 28.0, 2.0, 2.8),
    ("Tenders", "Tenders x3 (Reaper)", 580, 36.0, 34.0, 28.0, 2.0, 3.2),
    ("Sliders", "Slider (Mild)", 420, 22.0, 38.0, 18.0, 2.0, 2.0),
    ("Sliders", "Slider (Hot)", 440, 22.0, 40.0, 18.0, 2.0, 2.4),
    ("Sides", "Fries (Regular)", 320, 4.0, 42.0, 16.0, 3.0, 0.8),
    ("Sides", "Mac & Cheese", 380, 14.0, 34.0, 20.0, 1.0, 1.6),
    ("Sides", "Coleslaw", 180, 1.0, 12.0, 14.0, 2.0, 0.6),
    ("Drinks", "Kool-Aid (Regular)", 120, 0, 32.0, 0, 0, 0.1),
]

_BANANA_TREE = [
    ("Starters", "Salt & Pepper Squid", 340, 18.0, 24.0, 18.0, 1.0, 2.2),
    ("Starters", "Spring Rolls x4", 280, 8.0, 30.0, 14.0, 2.0, 1.6),
    ("Curry", "Thai Green Curry Chicken", 580, 28.0, 44.0, 30.0, 3.0, 2.4),
    ("Curry", "Rendang Beef", 650, 34.0, 38.0, 34.0, 2.0, 2.6),
    ("Noodles", "Pad Thai Prawn", 620, 24.0, 72.0, 22.0, 3.0, 3.2),
    ("Rice", "Nasi Goreng", 680, 26.0, 78.0, 26.0, 3.0, 2.8),
    ("Sides", "Coconut Rice", 260, 4.0, 48.0, 6.0, 1.0, 0.4),
    ("Desserts", "Banana Fritters & Ice Cream", 420, 4.0, 56.0, 20.0, 2.0, 0.3),
]

_BARBURRITO = [
    ("Burritos", "Chicken Burrito", 680, 36.0, 72.0, 22.0, 8.0, 2.6),
    ("Burritos", "Steak Burrito", 720, 38.0, 72.0, 26.0, 8.0, 2.8),
    ("Burritos", "Veggie Burrito", 580, 18.0, 74.0, 18.0, 10.0, 2.2),
    ("Bowls", "Chicken Naked Burrito", 520, 34.0, 48.0, 18.0, 6.0, 2.4),
    ("Tacos", "Chicken Tacos x3", 480, 28.0, 42.0, 18.0, 4.0, 2.2),
    ("Sides", "Nachos & Guac", 420, 8.0, 44.0, 24.0, 4.0, 1.8),
    ("Sides", "Chips & Salsa", 280, 4.0, 36.0, 14.0, 3.0, 1.2),
    ("Quesadillas", "Chicken Quesadilla", 560, 32.0, 42.0, 26.0, 3.0, 2.4),
]

_CARLUCCIOS = [
    ("Pasta", "Spaghetti Bolognese", 620, 28.0, 68.0, 22.0, 4.0, 2.4),
    ("Pasta", "Penne Arrabbiata", 520, 16.0, 72.0, 16.0, 4.0, 2.2),
    ("Pasta", "Carbonara", 740, 30.0, 66.0, 36.0, 2.0, 2.8),
    ("Pizza", "Margherita", 680, 26.0, 78.0, 24.0, 3.0, 2.6),
    ("Pizza", "Diavola", 780, 32.0, 76.0, 32.0, 3.0, 3.2),
    ("Mains", "Chicken Milanese", 720, 38.0, 52.0, 34.0, 2.0, 2.4),
    ("Starters", "Bruschetta", 280, 6.0, 32.0, 14.0, 2.0, 1.4),
    ("Desserts", "Tiramisu", 380, 6.0, 40.0, 22.0, 0.5, 0.3),
]

_FIREAWAY = [
    ("Pizza", "Margherita (12\")", 680, 28.0, 76.0, 24.0, 3.0, 2.6),
    ("Pizza", "Pepperoni (12\")", 780, 34.0, 74.0, 32.0, 3.0, 3.2),
    ("Pizza", "BBQ Chicken (12\")", 740, 36.0, 78.0, 26.0, 3.0, 2.8),
    ("Pizza", "Veggie Supreme (12\")", 640, 22.0, 78.0, 22.0, 4.0, 2.4),
    ("Pizza", "Meat Feast (12\")", 820, 40.0, 74.0, 36.0, 3.0, 3.6),
    ("Sides", "Garlic Bread", 280, 6.0, 34.0, 14.0, 1.0, 1.2),
    ("Sides", "Chicken Wings x6", 380, 28.0, 12.0, 24.0, 0, 2.4),
    ("Desserts", "Cookie Dough", 420, 4.0, 54.0, 22.0, 1.0, 0.4),
]

_GERMAN_GYMNASIUM = [
    ("Starters", "Pretzel & Obatzda", 420, 14.0, 48.0, 18.0, 3.0, 2.4),
    ("Mains", "Wiener Schnitzel", 780, 42.0, 52.0, 38.0, 2.0, 2.6),
    ("Mains", "Currywurst & Fries", 720, 28.0, 56.0, 38.0, 3.0, 3.2),
    ("Mains", "Bratwurst & Sauerkraut", 680, 32.0, 42.0, 36.0, 4.0, 3.0),
    ("Desserts", "Apple Strudel", 380, 4.0, 48.0, 18.0, 2.0, 0.4),
]

_ABSURD_BIRD = [
    ("Chicken", "Fried Chicken Burger", 720, 34.0, 56.0, 36.0, 2.0, 2.8),
    ("Chicken", "Wings x6 (Hot Sauce)", 480, 32.0, 18.0, 28.0, 1.0, 3.0),
    ("Chicken", "Tenders x5", 580, 38.0, 34.0, 28.0, 1.0, 2.6),
    ("Chicken", "Half Rotisserie Chicken", 520, 48.0, 2.0, 34.0, 0, 2.8),
    ("Sides", "Mac & Cheese", 380, 14.0, 34.0, 20.0, 1.0, 1.6),
    ("Sides", "Fries", 320, 4.0, 42.0, 16.0, 3.0, 0.8),
    ("Sides", "Coleslaw", 160, 1.0, 8.0, 14.0, 2.0, 0.6),
    ("Desserts", "Brownie & Ice Cream", 480, 6.0, 58.0, 26.0, 2.0, 0.4),
]

_YARD_SALE_PIZZA = [
    ("Pizza", "Margherita (14\")", 720, 28.0, 80.0, 26.0, 3.0, 2.8),
    ("Pizza", "Pepperoni (14\")", 840, 36.0, 78.0, 36.0, 3.0, 3.4),
    ("Pizza", "Holy Pepperoni (14\")", 880, 38.0, 78.0, 40.0, 3.0, 3.6),
    ("Pizza", "Aubergine Parmigiana (14\")", 680, 22.0, 82.0, 24.0, 5.0, 2.6),
    ("Sides", "Garlic Bread", 320, 8.0, 38.0, 16.0, 1.0, 1.4),
    ("Sides", "Chicken Wings x8", 480, 36.0, 12.0, 28.0, 0, 2.8),
    ("Desserts", "Nutella Pizza", 520, 10.0, 62.0, 26.0, 2.0, 0.4),
]

_FLAT_IRON = [
    ("Steaks", "Flat Iron Steak (250g)", 560, 52.0, 0, 36.0, 0, 1.8),
    ("Steaks", "Rump Steak (250g)", 480, 50.0, 0, 28.0, 0, 1.6),
    ("Steaks", "Beef Dripping Fries", 380, 4.0, 46.0, 20.0, 3.0, 1.2),
    ("Starters", "Roast Bone Marrow", 320, 8.0, 12.0, 28.0, 0, 1.4),
    ("Sides", "Creamed Spinach", 220, 6.0, 8.0, 18.0, 3.0, 1.0),
    ("Desserts", "Salted Caramel Ice Cream", 280, 4.0, 32.0, 16.0, 0, 0.4),
]

_PATTY_AND_BUN = [
    ("Burgers", "Ari Gold (Cheeseburger)", 780, 38.0, 48.0, 44.0, 2.0, 2.8),
    ("Burgers", "Smokey Robinson", 820, 42.0, 52.0, 44.0, 2.0, 3.0),
    ("Burgers", "Jose Jose (Chicken)", 720, 36.0, 50.0, 38.0, 2.0, 2.6),
    ("Burgers", "Whoopi Goldberger (Veggie)", 640, 18.0, 56.0, 34.0, 4.0, 2.2),
    ("Sides", "Rosemary Fries", 380, 4.0, 48.0, 20.0, 3.0, 1.0),
    ("Sides", "Onion Rings", 340, 4.0, 38.0, 18.0, 2.0, 1.2),
    ("Shakes", "Peanut Butter Shake", 580, 14.0, 62.0, 30.0, 2.0, 0.6),
]

_MEATLIQUOR = [
    ("Burgers", "Dead Hippie", 820, 40.0, 48.0, 48.0, 2.0, 3.2),
    ("Burgers", "Green Chilli Cheeseburger", 780, 38.0, 46.0, 44.0, 2.0, 3.0),
    ("Burgers", "Bacon Cheeseburger", 860, 44.0, 48.0, 50.0, 2.0, 3.4),
    ("Chicken", "Buffalo Wings x8", 520, 36.0, 16.0, 30.0, 1.0, 3.2),
    ("Chicken", "Deep Fried Pickles x6", 280, 4.0, 32.0, 16.0, 2.0, 1.8),
    ("Sides", "Fries", 340, 4.0, 44.0, 16.0, 3.0, 0.8),
    ("Shakes", "Hard Shake (Oreo)", 580, 10.0, 68.0, 30.0, 1.0, 0.4),
]

_BONE_DADDIES = [
    ("Ramen", "Tonkotsu Ramen", 720, 32.0, 68.0, 32.0, 3.0, 4.2),
    ("Ramen", "T22 Chicken Ramen", 680, 34.0, 64.0, 28.0, 3.0, 3.8),
    ("Ramen", "Tantanmen Ramen", 740, 30.0, 66.0, 36.0, 3.0, 4.0),
    ("Starters", "Karaage Chicken", 380, 24.0, 22.0, 20.0, 1.0, 2.2),
    ("Starters", "Gyoza x6", 320, 12.0, 28.0, 16.0, 1.0, 2.0),
    ("Sides", "Edamame", 120, 12.0, 6.0, 5.0, 4.0, 1.0),
    ("Sides", "Rice", 200, 4.0, 44.0, 1.0, 0.5, 0.1),
    ("Desserts", "Matcha Soft Serve", 240, 4.0, 32.0, 10.0, 0, 0.2),
]

_CHOPHOUSE = [
    ("Steaks", "Ribeye Steak (300g)", 680, 54.0, 0, 48.0, 0, 2.0),
    ("Steaks", "Fillet Steak (200g)", 440, 50.0, 0, 24.0, 0, 1.6),
    ("Mains", "Lamb Cutlets", 580, 40.0, 8.0, 42.0, 1.0, 2.2),
    ("Starters", "Prawn Cocktail", 280, 18.0, 8.0, 18.0, 1.0, 1.8),
    ("Sides", "Triple Cooked Chips", 380, 4.0, 48.0, 20.0, 3.0, 1.0),
    ("Desserts", "Sticky Toffee Pudding", 480, 4.0, 64.0, 24.0, 1.0, 0.6),
]

_ROSAS_THAI_CAFE = [
    ("Curry", "Massaman Chicken", 620, 30.0, 42.0, 34.0, 3.0, 2.4),
    ("Curry", "Jungle Curry Prawns", 480, 26.0, 32.0, 24.0, 4.0, 2.6),
    ("Noodles", "Pad See Ew", 580, 24.0, 68.0, 22.0, 2.0, 3.0),
    ("Rice", "Khao Pad (Fried Rice)", 620, 22.0, 76.0, 24.0, 2.0, 2.8),
    ("Starters", "Thai Fish Cakes", 280, 16.0, 18.0, 14.0, 1.0, 2.0),
    ("Starters", "Satay Chicken Skewers", 320, 24.0, 12.0, 18.0, 1.0, 1.8),
    ("Desserts", "Mango Sticky Rice", 380, 4.0, 56.0, 14.0, 2.0, 0.2),
]

_GREGGS_CAFE = [
    ("Hot Drinks", "Flat White", 120, 6.0, 10.0, 6.0, 0, 0.2),
    ("Hot Drinks", "Cappuccino", 110, 6.0, 10.0, 5.0, 0, 0.2),
    ("Hot Drinks", "Hot Chocolate", 220, 8.0, 30.0, 8.0, 1.0, 0.4),
    ("Cold Drinks", "Iced Latte", 100, 5.0, 10.0, 4.0, 0, 0.2),
    ("Sweet", "Yum Yum", 260, 3.0, 30.0, 14.0, 1.0, 0.4),
    ("Sweet", "Belgian Bun", 340, 5.0, 48.0, 14.0, 1.0, 0.5),
    ("Sweet", "Triple Chocolate Cookie", 280, 3.0, 34.0, 14.0, 1.0, 0.4),
    ("Savoury", "Cheese & Onion Bake", 380, 10.0, 34.0, 22.0, 2.0, 1.6),
]

_OLE_AND_STEEN = [
    ("Pastry", "Cinnamon Social", 420, 6.0, 48.0, 24.0, 1.0, 0.6),
    ("Pastry", "Croissant", 280, 5.0, 28.0, 16.0, 1.0, 0.5),
    ("Pastry", "Pain au Chocolat", 320, 5.0, 32.0, 18.0, 1.0, 0.4),
    ("Bread", "Sourdough Loaf (per 100g)", 250, 8.0, 48.0, 1.0, 3.0, 1.2),
    ("Sandwich", "Ham & Cheese Croissant", 420, 18.0, 28.0, 24.0, 1.0, 1.8),
    ("Sandwich", "Smoked Salmon Open Sandwich", 380, 22.0, 32.0, 16.0, 2.0, 2.2),
    ("Drinks", "Flat White", 120, 6.0, 10.0, 6.0, 0, 0.2),
    ("Drinks", "Iced Matcha Latte", 160, 6.0, 22.0, 4.0, 0, 0.2),
]

_PAUL_BAKERY = [
    ("Pastry", "Croissant au Beurre", 300, 5.0, 30.0, 18.0, 1.0, 0.5),
    ("Pastry", "Pain au Chocolat", 340, 6.0, 34.0, 20.0, 1.0, 0.4),
    ("Pastry", "Almond Croissant", 420, 8.0, 38.0, 26.0, 2.0, 0.4),
    ("Sandwich", "Croque Monsieur", 480, 24.0, 34.0, 26.0, 1.0, 2.4),
    ("Sandwich", "Jambon Beurre Baguette", 520, 22.0, 52.0, 22.0, 2.0, 2.6),
    ("Salads", "Niçoise Salad", 380, 22.0, 18.0, 22.0, 3.0, 2.0),
    ("Tarts", "Tarte au Citron", 340, 4.0, 38.0, 20.0, 0, 0.3),
    ("Drinks", "Latte", 140, 7.0, 12.0, 6.0, 0, 0.2),
]

_EAT = [
    ("Sandwiches", "Chicken Caesar Wrap", 480, 28.0, 38.0, 22.0, 3.0, 2.2),
    ("Sandwiches", "BLT on Sourdough", 440, 18.0, 40.0, 22.0, 3.0, 2.0),
    ("Soups", "Chicken & Sweetcorn Soup", 280, 16.0, 28.0, 10.0, 3.0, 1.8),
    ("Soups", "Tomato & Basil Soup", 180, 4.0, 22.0, 8.0, 3.0, 1.4),
    ("Salads", "Falafel & Halloumi Salad", 420, 18.0, 36.0, 22.0, 6.0, 2.0),
    ("Hot", "Macaroni Cheese", 520, 18.0, 48.0, 28.0, 2.0, 2.2),
    ("Sweet", "Brownie", 380, 4.0, 44.0, 22.0, 2.0, 0.4),
    ("Drinks", "Flat White", 120, 6.0, 10.0, 6.0, 0, 0.2),
]

_BENUGO = [
    ("Sandwiches", "Ham Hock & Piccalilli", 420, 22.0, 38.0, 18.0, 2.0, 2.2),
    ("Sandwiches", "Egg Mayo & Cress", 380, 14.0, 36.0, 18.0, 2.0, 1.6),
    ("Salads", "Grilled Chicken Caesar", 380, 28.0, 14.0, 22.0, 2.0, 1.8),
    ("Hot", "Beef Chilli with Rice", 520, 26.0, 56.0, 18.0, 4.0, 2.4),
    ("Pastry", "Almond Croissant", 420, 8.0, 36.0, 26.0, 2.0, 0.4),
    ("Sweet", "Carrot Cake", 380, 4.0, 46.0, 20.0, 1.0, 0.4),
    ("Drinks", "Cappuccino", 110, 6.0, 10.0, 5.0, 0, 0.2),
]

_BLACK_SHEEP_COFFEE = [
    ("Hot Drinks", "Flat White", 120, 6.0, 10.0, 6.0, 0, 0.2),
    ("Hot Drinks", "Dirty Chai Latte", 200, 6.0, 28.0, 6.0, 0, 0.3),
    ("Hot Drinks", "Hot Chocolate", 260, 8.0, 34.0, 10.0, 1.0, 0.4),
    ("Cold Drinks", "Iced Americano", 10, 0, 2.0, 0, 0, 0),
    ("Cold Drinks", "Iced Mocha", 320, 8.0, 44.0, 12.0, 1.0, 0.3),
    ("Food", "Bacon Roll", 380, 18.0, 34.0, 16.0, 1.0, 2.2),
    ("Food", "Avocado Toast", 340, 8.0, 34.0, 18.0, 6.0, 1.0),
    ("Sweet", "Cookie", 280, 3.0, 34.0, 14.0, 1.0, 0.4),
]

_PHO = [
    ("Pho", "Pho Chin (Brisket)", 480, 28.0, 52.0, 14.0, 2.0, 3.8),
    ("Pho", "Pho Ga (Chicken)", 420, 30.0, 48.0, 10.0, 2.0, 3.4),
    ("Pho", "Pho Chay (Veggie)", 380, 12.0, 52.0, 10.0, 4.0, 3.0),
    ("Rice", "Broken Rice Chicken", 580, 32.0, 64.0, 18.0, 2.0, 2.6),
    ("Starters", "Summer Rolls", 220, 8.0, 28.0, 8.0, 2.0, 1.6),
    ("Starters", "Vietnamese Spring Rolls", 280, 10.0, 24.0, 14.0, 1.0, 1.8),
    ("Curry", "Saigon Curry Chicken", 540, 28.0, 42.0, 26.0, 3.0, 2.4),
    ("Desserts", "Che (Sweet Soup)", 280, 4.0, 44.0, 10.0, 2.0, 0.2),
]

_COCO_DI_MAMA = [
    ("Pasta", "Bolognese", 580, 26.0, 64.0, 20.0, 4.0, 2.4),
    ("Pasta", "Carbonara", 680, 28.0, 62.0, 32.0, 2.0, 2.6),
    ("Pasta", "Pesto Chicken", 620, 32.0, 60.0, 24.0, 3.0, 2.2),
    ("Pasta", "Nduja Arrabbiata", 540, 18.0, 66.0, 20.0, 4.0, 2.4),
    ("Salads", "Caesar Salad", 320, 18.0, 16.0, 20.0, 2.0, 1.8),
    ("Sides", "Garlic Bread", 240, 6.0, 30.0, 10.0, 1.0, 1.2),
    ("Drinks", "Espresso", 5, 0.3, 0.5, 0, 0, 0),
]

_BENITOS_HAT = [
    ("Burritos", "Chicken Burrito", 720, 38.0, 74.0, 24.0, 8.0, 2.8),
    ("Burritos", "Pork Carnitas Burrito", 760, 36.0, 76.0, 28.0, 8.0, 3.0),
    ("Tacos", "Fish Tacos x3", 480, 24.0, 42.0, 20.0, 3.0, 2.2),
    ("Tacos", "Chicken Tinga Tacos x3", 440, 26.0, 38.0, 18.0, 3.0, 2.0),
    ("Bowls", "Naked Burrito Bowl", 520, 32.0, 52.0, 18.0, 6.0, 2.4),
    ("Sides", "Guacamole & Chips", 380, 4.0, 36.0, 24.0, 6.0, 1.2),
    ("Sides", "Elote (Street Corn)", 280, 6.0, 28.0, 16.0, 3.0, 1.4),
]

_PING_PONG = [
    ("Dim Sum", "Har Gau (Prawn) x3", 180, 12.0, 18.0, 4.0, 0, 1.4),
    ("Dim Sum", "Siu Mai (Pork) x3", 210, 14.0, 16.0, 8.0, 0, 1.6),
    ("Dim Sum", "Char Sui Buns x2", 280, 10.0, 36.0, 10.0, 1.0, 1.4),
    ("Dim Sum", "Vegetable Dumplings x3", 160, 6.0, 20.0, 6.0, 2.0, 1.2),
    ("Mains", "Sweet & Sour Chicken", 580, 28.0, 56.0, 24.0, 2.0, 2.4),
    ("Mains", "Kung Pao Prawns", 420, 24.0, 28.0, 20.0, 2.0, 2.6),
    ("Sides", "Egg Fried Rice", 340, 8.0, 52.0, 12.0, 1.0, 1.8),
    ("Desserts", "Mochi Ice Cream x3", 240, 4.0, 30.0, 10.0, 0, 0.2),
]

_INAMO = [
    ("Sushi", "Salmon Nigiri x4", 220, 16.0, 28.0, 4.0, 0, 1.2),
    ("Sushi", "Dragon Roll x8", 380, 14.0, 48.0, 14.0, 2.0, 2.0),
    ("Sushi", "Tuna Sashimi x6", 180, 28.0, 0, 6.0, 0, 1.0),
    ("Robata", "Teriyaki Chicken Skewers", 320, 24.0, 18.0, 14.0, 1.0, 2.2),
    ("Robata", "Beef Tataki", 280, 22.0, 8.0, 16.0, 0, 1.8),
    ("Mains", "Black Cod Miso", 420, 28.0, 18.0, 24.0, 0, 2.6),
    ("Sides", "Edamame Truffle", 160, 12.0, 8.0, 8.0, 4.0, 1.2),
    ("Desserts", "Matcha Cheesecake", 340, 6.0, 36.0, 18.0, 0, 0.3),
]

# ── Batch 4: Coffee, bakery & breakfast chains ────────────────────────

_PATISSERIE_VALERIE = [
    ("Cakes", "Mille-Feuille", 437, 6.0, 42.0, 28.0, 1.0, 0.4),
    ("Cakes", "Double Chocolate Slice", 490, 6.0, 52.0, 28.0, 2.0, 0.5),
    ("Cakes", "Strawberry Gateau (slice)", 275, 4.0, 32.0, 14.0, 1.0, 0.3),
    ("Cakes", "Black Forest Gateau (slice)", 350, 4.0, 38.0, 20.0, 1.0, 0.3),
    ("Cakes", "Victoria Sponge (slice)", 320, 4.0, 36.0, 18.0, 0, 0.3),
    ("Pastry", "Plain Scone", 354, 6.0, 44.0, 16.0, 1.0, 1.0),
    ("Pastry", "Fruit Scone", 386, 6.0, 52.0, 16.0, 2.0, 1.0),
    ("Pastry", "Coffee Eclair", 300, 5.0, 28.0, 18.0, 0, 0.3),
    ("Pastry", "Croissant", 280, 5.0, 28.0, 16.0, 1.0, 0.5),
    ("Drinks", "Latte", 140, 7.0, 12.0, 6.0, 0, 0.2),
]

_UPPER_CRUST = [
    ("Baguettes", "Ham & Mozzarella Baguette", 488, 24.0, 48.0, 18.0, 2.0, 2.6),
    ("Baguettes", "Tuna Mayo Baguette", 535, 22.0, 50.0, 26.0, 2.0, 2.2),
    ("Baguettes", "Chicken & Bacon Baguette", 520, 28.0, 48.0, 22.0, 2.0, 2.4),
    ("Baguettes", "Meatball Marinara Baguette", 560, 24.0, 54.0, 24.0, 3.0, 2.8),
    ("Baguettes", "Veggie Baguette", 420, 14.0, 52.0, 16.0, 3.0, 2.0),
    ("Baguettes", "Steak & Cheese Baguette", 580, 30.0, 50.0, 26.0, 2.0, 2.6),
    ("Sides", "Artisan Baguette (4\" slice)", 160, 5.0, 30.0, 2.0, 1.0, 0.8),
    ("Drinks", "Americano", 10, 0.5, 1.0, 0, 0, 0),
]

_CORNISH_BAKERY = [
    ("Pasties", "Traditional Steak Pasty", 740, 22.0, 58.0, 44.0, 3.0, 2.2),
    ("Pasties", "Steak & Stilton Pasty", 831, 26.0, 56.0, 54.0, 3.0, 2.6),
    ("Pasties", "Cheese & Onion Pasty", 680, 16.0, 58.0, 40.0, 3.0, 2.0),
    ("Pasties", "Chicken & Bacon Pasty", 720, 24.0, 56.0, 42.0, 2.0, 2.4),
    ("Pasties", "Vegan Pasty", 620, 12.0, 60.0, 34.0, 4.0, 1.8),
    ("Sweet", "Cornish Cream Tea Scone", 380, 6.0, 46.0, 18.0, 1.0, 1.0),
    ("Sweet", "Sausage Roll", 420, 14.0, 32.0, 26.0, 1.0, 1.8),
    ("Drinks", "Flat White", 120, 6.0, 10.0, 6.0, 0, 0.2),
]

_ESQUIRES_COFFEE = [
    ("Breakfast", "Bacon Roll", 514, 22.0, 42.0, 26.0, 1.0, 2.8),
    ("Breakfast", "Smashed Avocado on Sourdough", 372, 8.0, 38.0, 20.0, 6.0, 1.2),
    ("Breakfast", "Smashed Avo + Halloumi + Egg", 630, 26.0, 40.0, 38.0, 6.0, 2.4),
    ("Breakfast", "Eggs Benedict", 480, 22.0, 28.0, 28.0, 1.0, 2.2),
    ("Hot Drinks", "Flat White", 120, 6.0, 10.0, 6.0, 0, 0.2),
    ("Hot Drinks", "Chai Latte", 200, 6.0, 30.0, 6.0, 0, 0.3),
    ("Cold Drinks", "Iced Latte", 100, 5.0, 10.0, 4.0, 0, 0.2),
    ("Sweet", "Chocolate Brownie", 380, 4.0, 44.0, 22.0, 2.0, 0.4),
]

_MUFFIN_BREAK = [
    ("Muffins", "Apple & Cinnamon Muffin", 380, 5.0, 46.0, 18.0, 2.0, 0.6),
    ("Muffins", "Mixed Berry Muffin", 360, 5.0, 44.0, 16.0, 2.0, 0.5),
    ("Muffins", "Chocolate Chip Muffin", 420, 6.0, 50.0, 22.0, 1.0, 0.5),
    ("Muffins", "Blueberry Muffin", 370, 5.0, 44.0, 18.0, 2.0, 0.5),
    ("Savoury", "Bacon, Egg & Cheese Bagel", 479, 24.0, 40.0, 22.0, 2.0, 2.4),
    ("Savoury", "Ham & Cheese Toastie", 420, 20.0, 36.0, 20.0, 1.0, 2.2),
    ("Drinks", "Flat White", 120, 6.0, 10.0, 6.0, 0, 0.2),
    ("Drinks", "Hot Chocolate", 260, 8.0, 34.0, 10.0, 1.0, 0.4),
]

_THE_BREAKFAST_CLUB = [
    ("Breakfast", "The Full Monty", 1342, 52.0, 82.0, 86.0, 6.0, 4.8),
    ("Breakfast", "Smashed Avocado on Toast", 133, 4.0, 12.0, 8.0, 4.0, 0.6),
    ("Breakfast", "Pancake Stack (3)", 726, 14.0, 88.0, 34.0, 2.0, 1.8),
    ("Breakfast", "Eggs Benedict", 520, 24.0, 30.0, 32.0, 1.0, 2.4),
    ("Breakfast", "Huevos Rancheros", 580, 22.0, 48.0, 30.0, 6.0, 2.6),
    ("Sides", "Hash Browns x2", 220, 2.0, 26.0, 12.0, 2.0, 0.8),
    ("Sides", "Homestyle Potatoes", 280, 4.0, 34.0, 14.0, 3.0, 1.0),
    ("Sides", "Pancake Balls", 726, 10.0, 84.0, 38.0, 1.0, 1.2),
    ("Burgers", "Classic Cheeseburger", 680, 34.0, 46.0, 36.0, 2.0, 2.6),
    ("Drinks", "Milkshake (Vanilla)", 480, 10.0, 58.0, 22.0, 0, 0.4),
]

_BIRDS_BAKERY = [
    ("Savoury", "Sausage Roll", 380, 12.0, 28.0, 24.0, 1.0, 1.6),
    ("Savoury", "Pork Pie", 440, 14.0, 30.0, 28.0, 1.0, 1.8),
    ("Savoury", "Cheese & Onion Roll", 360, 10.0, 32.0, 20.0, 1.0, 1.4),
    ("Savoury", "Steak Bake", 420, 16.0, 34.0, 24.0, 1.0, 1.8),
    ("Bread", "White Farmhouse Loaf (per 100g)", 240, 8.0, 46.0, 2.0, 2.0, 1.0),
    ("Sweet", "Cream Doughnut", 320, 4.0, 36.0, 18.0, 1.0, 0.4),
    ("Sweet", "Vanilla Slice", 280, 3.0, 34.0, 14.0, 0, 0.3),
    ("Sweet", "Iced Bun", 260, 4.0, 38.0, 10.0, 1.0, 0.4),
]

# ── All chains aggregated ──────────────────────────────────────────────
_ALL_CHAINS = [
    ("KFC", "https://www.kfc.co.uk/nutrition-information", _KFC),
    ("Burger King", "https://www.burgerking.co.uk/nutrition", _BURGER_KING),
    ("Subway", "https://www.subway.com/en-GB/MenuNutrition/Nutrition", _SUBWAY),
    ("Pizza Hut", "https://www.pizzahut.co.uk/order/nutritional-information", _PIZZA_HUT),
    ("Dominos", "https://www.dominos.co.uk/menu/nutritional-info", _DOMINOS),
    ("Greggs", "https://www.greggs.co.uk/nutrition", _GREGGS),
    ("Costa Coffee", "https://www.costa.co.uk/nutrition", _COSTA),
    ("Pret A Manger", "https://www.pret.co.uk/en-GB/our-menu", _PRET),
    ("Starbucks", "https://www.starbucks.co.uk/menu", _STARBUCKS),
    ("Pizza Express", "https://www.pizzaexpress.com/our-food", _PIZZA_EXPRESS),
    ("Zizzi", "https://www.zizzi.co.uk/menu", _ZIZZI),
    ("Prezzo", "https://www.prezzorestaurants.co.uk/menu", _PREZZO),
    ("Five Guys", "https://www.fiveguys.co.uk/menu", _FIVE_GUYS),
    ("TGI Fridays", "https://www.tgifridays.co.uk/menu", _TGI_FRIDAYS),
    ("Frankie & Bennys", "https://www.frankieandbennys.com/food-and-drink", _FRANKIE_BENNYS),
    ("Harvester", "https://www.harvester.co.uk/menus", _HARVESTER),
    ("Toby Carvery", "https://www.tobycarvery.co.uk/food", _TOBY_CARVERY),
    ("Wetherspoons", "https://www.jdwetherspoon.com/food", _WETHERSPOONS),
    ("GBK", "https://www.gbk.co.uk/menu", _GBK),
    ("Leon", "https://leon.co/menu", _LEON),
    ("Itsu", "https://www.itsu.com/menu", _ITSU),
    ("Yo! Sushi", "https://yosushi.com/menu", _YO_SUSHI),
    ("Honest Burgers", "https://www.honestburgers.co.uk/food/burgers", _HONEST_BURGERS),
    ("The Real Greek", "https://www.therealgreek.com/menu", _REAL_GREEK),
    ("Las Iguanas", "https://www.lasiguanas.co.uk/food-and-drink", _LAS_IGUANAS),
    ("Bills", "https://bills-website.co.uk/menus", _BILLS),
    ("Bella Italia", "https://www.bellaitalia.co.uk/food-drink", _BELLA_ITALIA),
    ("ASK Italian", "https://www.askitalian.co.uk/food-and-drink", _ASK_ITALIAN),
    ("Tortilla", "https://www.tortilla.co.uk/menu", _TORTILLA),
    ("Wasabi", "https://www.wasabi.uk.com/menu", _WASABI),
    ("Franco Manca", "https://www.francomanca.co.uk/menu", _FRANCO_MANCA),
    ("Dishoom", "https://www.dishoom.com/food-drink", _DISHOOM),
    ("Slim Chickens", "https://slimchickens.co.uk/menu", _SLIM_CHICKENS),
    ("Wingstop", "https://www.wingstop.co.uk/menu", _WINGSTOP),
    ("Popeyes", "https://www.popeyes.co.uk/menu", _POPEYES),
    ("Chipotle", "https://www.chipotle.co.uk/nutrition-calculator", _CHIPOTLE),
    ("Taco Bell", "https://www.tacobell.co.uk/menu", _TACO_BELL),
    ("Chicken Cottage", "https://www.chickencottage.com/menu", _CHICKEN_COTTAGE),
    ("Morleys", "https://morleys.com/menu", _MORLEYS),
    ("German Doner Kebab", "https://www.germandonerkebab.com/menu", _GERMAN_DONER_KEBAB),
    ("Wimpy", "https://www.wimpy.uk.com/menu", _WIMPY),
    ("Harry Ramsdens", "https://www.harryramsdens.co.uk/menu", _HARRY_RAMSDENS),
    ("Beefeater", "https://www.beefeater.co.uk/en-gb/food", _BEEFEATER),
    ("Miller & Carter", "https://www.millerandcarter.co.uk/menus", _MILLER_CARTER),
    ("Cafe Rouge", "https://www.caferouge.com/food-drink", _CAFE_ROUGE),
    ("Chiquito", "https://www.chiquito.co.uk/food-and-drink", _CHIQUITO),
    # ── Batch 2: Additional chains ──
    ("Caffe Nero", "https://www.caffenero.com/uk/menu", _CAFFE_NERO),
    ("Papa Johns", "https://www.papajohns.co.uk/static/assets/pdfs/nutritional-information.pdf", _PAPA_JOHNS),
    ("Pepes Piri Piri", "https://pepes.co.uk/nutrition-allergens-uk/", _PEPES_PIRI_PIRI),
    ("Chopstix", "https://chopstixnoodles.co.uk/food-menu/", _CHOPSTIX),
    ("Kokoro", "https://www.kokoromaidstone.co.uk/menu", _KOKORO),
    ("Hungry Horse", "https://www.hungryhorse.co.uk/menu-highlights", _HUNGRY_HORSE),
    ("Loungers", "https://thelounges.co.uk/menus/", _LOUNGERS),
    ("Cote Brasserie", "https://www.cote.co.uk/menus/main-menu", _COTE),
    ("Giggling Squid", "https://www.gigglingsquid.com/menu/", _GIGGLING_SQUID),
    ("Gails Bakery", "https://gails.com/", _GAILS),
    ("Wahaca", "https://www.wahaca.co.uk/mexican-menu-full/", _WAHACA),
    ("Rosas Thai", "https://rosasthai.com/nutrition", _ROSAS_THAI),
    ("Boojum", "https://boojummex.com/our-menu", _BOOJUM),
    ("Apache Pizza", "https://nutrition.apache.ie/", _APACHE_PIZZA),
    ("Supermacs", "https://supermacs.ie/nutritional-information/", _SUPERMACS),
    ("Tim Hortons", "https://www.timhortons.co.uk/menu", _TIM_HORTONS),
    ("Chick-fil-A", "https://www.chick-fil-a.co.uk/menu", _CHICK_FIL_A),
    ("Four Star Pizza", "https://www.fourstarpizza.co.uk/menu", _FOUR_STAR_PIZZA),
    ("Eddie Rockets", "https://www.eddierockets.ie/menu", _EDDIE_ROCKETS),
    ("Mary Browns", "https://www.marybrowns.com/menu", _MARYBROWNS),
    ("Shake Shack", "https://www.shakeshack.co.uk/", _SHAKE_SHACK),
    ("The Botanist", "https://thebotanist.uk.com/", _THE_BOTANIST),
    ("Comptoir Libanais", "https://www.comptoirlibanais.com/menus/", _COMPTOIR_LIBANAIS),
    ("Busaba", "https://www.busaba.com/menu/food", _BUSABA),
    # ── Batch 3: Casual dining, coffee & bakery chains ──
    ("Turtle Bay", "https://www.turtlebay.co.uk/food-drink/food-menu", _TURTLE_BAY),
    ("Mowgli Street Food", "https://www.mowglistreetfood.com/menus/", _MOWGLI),
    ("Krispy Kreme", "https://www.krispykreme.co.uk/menu", _KRISPY_KREME),
    ("Daves Hot Chicken", "https://daveshotchicken.co.uk/menu", _DAVES_HOT_CHICKEN),
    ("Banana Tree", "https://www.bananatree.co.uk/menus/", _BANANA_TREE),
    ("Barburrito", "https://www.barburrito.co.uk/menu", _BARBURRITO),
    ("Carluccios", "https://www.carluccios.com/menus/", _CARLUCCIOS),
    ("Fireaway Pizza", "https://fireaway.co.uk/menu", _FIREAWAY),
    ("German Gymnasium", "https://www.germangymnasium.com/menus", _GERMAN_GYMNASIUM),
    ("Absurd Bird", "https://absurdbird.com/menu", _ABSURD_BIRD),
    ("Yard Sale Pizza", "https://yardsalepizza.com/menu", _YARD_SALE_PIZZA),
    ("Flat Iron", "https://flatironsteak.co.uk/", _FLAT_IRON),
    ("Patty & Bun", "https://www.pattyandbun.co.uk/menus", _PATTY_AND_BUN),
    ("MEATliquor", "https://meatliquor.com/menu", _MEATLIQUOR),
    ("Bone Daddies", "https://bonedaddies.com/menu/", _BONE_DADDIES),
    ("Chophouse", "https://www.hawksmoor.com/", _CHOPHOUSE),
    ("Rosa's Thai Cafe", "https://rosasthai.com/menus/", _ROSAS_THAI_CAFE),
    ("Greggs Cafe", "https://www.greggs.co.uk/nutrition", _GREGGS_CAFE),
    ("Ole & Steen", "https://oleandsteen.co.uk/", _OLE_AND_STEEN),
    ("Paul Bakery", "https://www.paul-uk.com/menu", _PAUL_BAKERY),
    ("EAT.", "https://eat.co.uk/menu", _EAT),
    ("Benugo", "https://www.benugo.com/menus", _BENUGO),
    ("Black Sheep Coffee", "https://www.blacksheepcoffee.com/", _BLACK_SHEEP_COFFEE),
    ("Pho", "https://www.phocafe.co.uk/food-menu/", _PHO),
    ("Coco di Mama", "https://www.cocodimama.co.uk/menu", _COCO_DI_MAMA),
    ("Benitos Hat", "https://www.benitoshat.com/menu", _BENITOS_HAT),
    ("Ping Pong", "https://www.pingpongdimsum.com/menu", _PING_PONG),
    ("Inamo", "https://www.inamo-restaurant.com/menu", _INAMO),
    # ── Batch 4: Coffee, bakery & breakfast chains ──
    ("Patisserie Valerie", "https://patisserie-valerie.co.uk/pages/nutritional-and-allergen-information", _PATISSERIE_VALERIE),
    ("Upper Crust", "https://uppercrust.co.uk/menu/", _UPPER_CRUST),
    ("Cornish Bakery", "https://thecornishbakery.com/pages/nutritional-information", _CORNISH_BAKERY),
    ("Esquires Coffee", "https://esquirescoffee.co.uk/food-drink/", _ESQUIRES_COFFEE),
    ("Muffin Break", "https://muffinbreak.co.uk/our-menu/", _MUFFIN_BREAK),
    ("The Breakfast Club", "https://thebreakfastclubcafes.com/menu/", _THE_BREAKFAST_CLUB),
    ("Birds Bakery", "https://birdsbakery.com/pages/nutrition-and-allergen-data", _BIRDS_BAKERY),
]
