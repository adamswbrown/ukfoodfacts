"""
Shared dietary flag inference for all scrapers.
Infers vegan/vegetarian/gluten_free from item names, descriptions, and source tags.
"""


# Keywords that strongly indicate a vegan item
_VEGAN_KEYWORDS = [
    "(vegan)", "(v)", "plant-based", "plant based",
    "mcplant", "vegan burger", "vegan wrap", "vegan",
]

# Keywords indicating vegetarian (but not necessarily vegan)
_VEGETARIAN_KEYWORDS = [
    "(vegetarian)", "(ve)", "veggie", "vegetable wrap",
    "vegetable gyoza", "veggie supreme", "veggie delite",
    "margherita", "halloumi", "mac & cheese", "mac and cheese",
    "mushroom risotto", "arrabbiata", "arrabiata",
]

# Items that are inherently vegan by nature
_VEGAN_ITEMS = [
    "edamame", "steamed rice", "rice", "chips", "fries",
    "corn on the cob", "tenderstem broccoli", "broccoli",
    "garden salad", "side salad", "spicy rice",
    "houmous", "hummus", "olives", "spicy mixed olives",
    "padron peppers", "patatas bravas",
    "garlic bread",  # typically vegan at chain restaurants
    "hash brown", "corn cups",
    "onion rings", "onion bhaji",
    "spring rolls", "thai spring rolls",
    "noodles", "bang bang cauliflower",
]

# Items that are inherently vegetarian (contain dairy/eggs but no meat)
_VEGETARIAN_ITEMS = [
    "mozzarella dippers", "halloumi sticks", "halloumi fries",
    "cheese pizza", "four cheese",
    "coleslaw", "rainbow slaw",
    "pizza margherita",
    "bruschetta", "arancini",
    "mochi ice cream",
]

# Meat/fish keywords that disqualify vegan/vegetarian
_MEAT_KEYWORDS = [
    "chicken", "beef", "pork", "lamb", "steak", "bacon",
    "ham", "duck", "turkey", "sausage", "gammon",
    "fish", "cod", "haddock", "salmon", "prawn", "shrimp",
    "lobster", "crab", "squid", "scallop", "mussel", "oyster",
    "seafood", "anchov", "pepperoni", "chorizo", "nduja",
    "mcnugget", "nugget", "wing", "drumstick", "thigh",
    "breast", "fillet", "ribeye", "sirloin", "venison",
    "haggis", "bone marrow", "wagyu", "iberico",
    "meatball", "bolognese", "carbonara", "big mac",
    "quarter pounder", "cheeseburger", "hamburger",
    "filet-o-fish", "mcchicken", "crispy mcbacon",
    "hot wings", "zinger", "popcorn chicken",
    "selects", "whopper",  # meat burgers
]

# Gluten-free keywords
_GF_KEYWORDS = [
    "gluten-free", "gluten free", "(gf)",
]


def infer_dietary_flags(item_name, description="", source_tags=None):
    """
    Infer dietary flags from item name, description, and optional source tags.

    Returns a list like ["vegan"], ["vegetarian"], ["vegan", "gluten_free"], etc.
    Only tags items we're reasonably confident about.
    """
    flags = []
    name_lower = item_name.lower()
    desc_lower = (description or "").lower()
    combined = name_lower + " " + desc_lower

    # Check source tags first (most reliable signal)
    if source_tags:
        tags_lower = [str(t).lower() for t in source_tags]
        if any(t in ("vegan", "plant-based") for t in tags_lower):
            flags.append("vegan")
        if any(t in ("vegetarian",) for t in tags_lower):
            flags.append("vegetarian")
        if any(t in ("gluten-free", "gf", "gluten_free") for t in tags_lower):
            flags.append("gluten_free")
        # If we got flags from source tags, trust them and return
        if flags:
            return flags

    has_meat = any(kw in combined for kw in _MEAT_KEYWORDS)

    # Check explicit vegan keywords in name (e.g. "(Vegan)" in the name)
    if any(kw in combined for kw in _VEGAN_KEYWORDS) and not has_meat:
        flags.append("vegan")
    # Check if it's an inherently vegan item
    elif not has_meat and any(name_lower.strip() == kw or name_lower.startswith(kw + " ") for kw in _VEGAN_ITEMS):
        flags.append("vegan")

    # Check vegetarian if not already vegan
    if "vegan" not in flags and not has_meat:
        if any(kw in combined for kw in _VEGETARIAN_KEYWORDS):
            flags.append("vegetarian")
        elif any(kw in name_lower for kw in _VEGETARIAN_ITEMS):
            flags.append("vegetarian")

    # Vegan implies vegetarian — but we don't double-tag, vegan is sufficient

    # Gluten-free
    if any(kw in combined for kw in _GF_KEYWORDS):
        flags.append("gluten_free")

    return flags
