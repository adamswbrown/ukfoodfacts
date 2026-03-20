"""
Shared dietary flag inference for all scrapers.
Infers vegan/vegetarian/gluten_free from item names, descriptions, and source tags.
"""


def _word_match(text, keyword):
    """Check if keyword appears as a distinct word/phrase in text."""
    text = text.strip()
    if text == keyword:
        return True
    if text.startswith(keyword + " ") or text.endswith(" " + keyword):
        return True
    if " " + keyword + " " in text:
        return True
    # Also match when keyword is followed by punctuation or parenthetical
    for sep in [",", ".", "(", ")", "&", "/", "-", "'"]:
        if keyword + sep in text or sep + keyword in text:
            return True
    return False


def _is_primary_vegan_item(name_lower, vegan_items):
    """
    Check if a vegan item keyword is the primary subject of the dish name,
    not just a side mentioned after '&' or 'with' (e.g. "Burger & Fries"
    should NOT match as vegan even though "fries" is vegan).
    """
    # Split on common conjunctions that join a main dish with a side
    for sep in [" & ", " and ", " with ", " w/ "]:
        if sep in name_lower:
            primary = name_lower.split(sep)[0].strip()
            # If the vegan item only appears in the secondary part, skip
            if any(_word_match(primary, kw) for kw in vegan_items):
                return True
            # Check if the primary part itself looks like a non-vegan dish
            # (e.g. "burger", "pie", "stew") — in that case, don't match
            if not any(_word_match(name_lower.split(sep)[-1].strip(), kw) for kw in vegan_items):
                return False
            # The vegan item is only in the secondary part
            return False
    # No conjunction — check the full name
    return any(_word_match(name_lower, kw) for kw in vegan_items)


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
    "paneer", "cheese toastie", "four cheese",
    "vegetable curry", "vegetable soup",
]

# Items/words that are inherently vegan by nature — matched with word boundaries
_VEGAN_ITEMS = [
    "edamame", "steamed rice", "plain rice", "pilau rice",
    "basmati rice", "spicy rice", "rice",
    "chips", "fries", "frites", "sweet potato fries",
    "corn on the cob", "tenderstem broccoli", "broccoli",
    "garden salad", "side salad", "garden vegetables",
    "houmous", "hummus", "hummus & bread",
    "olives", "spicy mixed olives",
    "padron peppers", "patatas bravas",
    "garlic bread",
    "hash brown", "hash browns", "corn cups",
    "onion rings", "onion bhaji",
    "spring rolls", "thai spring rolls",
    "noodles", "bang bang cauliflower",
    "tofu", "falafel",
    "hoppers", "string hoppers",
    "bruschetta",
    "chip shop curry sauce",
    "penne arrabbiata", "penne arrabiata",
]

# Items that are inherently vegetarian (contain dairy/eggs but no meat)
_VEGETARIAN_ITEMS = [
    "mozzarella dippers", "mozzarella sticks",
    "halloumi sticks", "halloumi fries", "halloumi burger",
    "cheese pizza", "four cheese",
    "coleslaw", "rainbow slaw",
    "pizza margherita",
    "arancini",
    "mochi ice cream",
    "loaded nachos", "nachos",
    "mac & cheese",
    "onion rings",
    "veggie supreme",
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
    "selects",
    "ribs", "pulled pork", "brisket", "scampi",
    "hake", "sea bass", "monkfish", "halibut",
    "mussels", "moules", "oysters", "scallops",
    "tartare", "mixed grill", "carvery",
    "roast beef", "roast chicken", "roast lamb",
    "katsu",  # usually chicken katsu
]

# Dairy/egg keywords that block vegan (but not vegetarian)
_DAIRY_KEYWORDS = [
    "halloumi", "cheese", "cheesy", "mozzarella", "cheddar", "parmesan",
    "cream", "yoghurt", "yogurt", "custard", "butter",
    "paneer", "egg ", "eggs", "omelette",
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
    has_dairy = any(kw in combined for kw in _DAIRY_KEYWORDS)
    explicit_vegan = any(kw in combined for kw in _VEGAN_KEYWORDS)

    # "Loaded" items (loaded fries, loaded nachos) typically have non-vegan toppings
    is_loaded = "loaded" in name_lower

    # Explicit vegan label overrides meat keywords (e.g. "Plant-Based Whopper")
    if explicit_vegan:
        flags.append("vegan")
    # Check if it's an inherently vegan item (must be the primary subject)
    elif not has_meat and not has_dairy and not is_loaded and _is_primary_vegan_item(name_lower, _VEGAN_ITEMS):
        flags.append("vegan")

    # Check vegetarian if not already vegan
    if "vegan" not in flags and not has_meat:
        if any(kw in combined for kw in _VEGETARIAN_KEYWORDS):
            flags.append("vegetarian")
        elif any(_word_match(name_lower, kw) for kw in _VEGETARIAN_ITEMS):
            flags.append("vegetarian")

    # Vegan implies vegetarian — but we don't double-tag, vegan is sufficient

    # Gluten-free
    if any(kw in combined for kw in _GF_KEYWORDS):
        flags.append("gluten_free")

    return flags
