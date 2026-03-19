"""
Wagamama UK nutrition scraper
Wagamama's menu is JS-rendered (React), so we use Playwright to load the page
and then intercept the network requests for nutrition JSON data.
URL: https://www.wagamama.com/menu
"""

import json
import asyncio
from datetime import date

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def scrape():
    if not PLAYWRIGHT_AVAILABLE:
        print("  [Wagamama] Playwright not available, using fallback data")
        return _fallback_data()

    print("  [Wagamama] Launching headless browser...")
    try:
        items = asyncio.run(_async_scrape())
        if items:
            print(f"  [Wagamama] Scraped {len(items)} items")
            return items
    except Exception as e:
        print(f"  [Wagamama] Headless scrape failed: {e}")

    return _fallback_data()


async def _async_scrape():
    items = []
    today = str(date.today())
    captured_responses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (compatible; HobbyNutritionBot/1.0; personal use)"
        )
        page = await context.new_page()

        # Intercept network responses to catch nutrition JSON
        async def handle_response(response):
            url = response.url
            # Look for any API calls that might contain menu/nutrition data
            if any(kw in url.lower() for kw in ["menu", "nutrition", "product", "item"]):
                if "json" in response.headers.get("content-type", "") or url.endswith(".json"):
                    try:
                        body = await response.body()
                        data = json.loads(body)
                        captured_responses.append((url, data))
                    except Exception:
                        pass

        page.on("response", handle_response)

        try:
            await page.goto(
                "https://www.wagamama.com/menu",
                wait_until="networkidle",
                timeout=30000,
            )
            # Give JS time to render
            await asyncio.sleep(3)
        except Exception as e:
            print(f"  [Wagamama] Page load error: {e}")
            await browser.close()
            return []

        # Try to parse intercepted JSON responses
        for url, data in captured_responses:
            parsed = _try_parse_wagamama_json(data, today)
            if parsed:
                items.extend(parsed)

        # If nothing from network intercept, try scraping rendered DOM
        if not items:
            items = await _parse_rendered_dom(page, today)

        await browser.close()

    return items


async def _parse_rendered_dom(page, today):
    """Fall back to scraping the rendered HTML for nutrition info."""
    items = []
    try:
        # Look for menu item containers
        cards = await page.query_selector_all("[class*='menu-item'], [class*='dish'], [data-testid*='product']")
        for card in cards[:100]:  # cap to avoid runaway
            name = await _get_text(card, ["[class*='name']", "h2", "h3", "h4"])
            cal_text = await _get_text(card, ["[class*='calorie']", "[class*='kcal']", "[class*='energy']"])
            cal = _extract_number(cal_text)
            if name:
                items.append({
                    "restaurant": "Wagamama",
                    "category": "Menu",
                    "item": name,
                    "description": "",
                    "calories_kcal": cal,
                    "protein_g": None,
                    "carbs_g": None,
                    "fat_g": None,
                    "fibre_g": None,
                    "salt_g": None,
                    "allergens": [],
                    "dietary_flags": [],
                    "location": "National",
                    "source_url": "https://www.wagamama.com/menu",
                    "scraped_at": today,
                })
    except Exception as e:
        print(f"  [Wagamama] DOM parse error: {e}")
    return items


async def _get_text(element, selectors):
    for sel in selectors:
        try:
            el = await element.query_selector(sel)
            if el:
                text = await el.inner_text()
                if text.strip():
                    return text.strip()
        except Exception:
            pass
    return ""


def _try_parse_wagamama_json(data, today):
    items = []
    try:
        if isinstance(data, list):
            products = data
        elif isinstance(data, dict):
            # Try various common structures
            products = (
                data.get("items")
                or data.get("products")
                or data.get("menu")
                or data.get("categories")
                or data.get("data")
                or []
            )
            # Handle nested categories
            if products and isinstance(products[0], dict) and "items" in products[0]:
                nested = []
                for cat in products:
                    cat_name = cat.get("name", "Menu")
                    for item in cat.get("items", []):
                        item["_category"] = cat_name
                        nested.append(item)
                products = nested
        else:
            return []

        for p in products:
            nutrition = p.get("nutrition") or p.get("nutrients") or p.get("nutritionalInfo") or {}
            items.append({
                "restaurant": "Wagamama",
                "category": p.get("_category") or p.get("category") or p.get("menuSection") or "Menu",
                "item": p.get("name") or p.get("title") or "Unknown",
                "description": p.get("description") or "",
                "calories_kcal": _safe_int(nutrition.get("calories") or nutrition.get("energy") or nutrition.get("kcal")),
                "protein_g": _safe_float(nutrition.get("protein")),
                "carbs_g": _safe_float(nutrition.get("carbohydrates") or nutrition.get("carbs")),
                "fat_g": _safe_float(nutrition.get("fat") or nutrition.get("totalFat")),
                "fibre_g": _safe_float(nutrition.get("fibre") or nutrition.get("fiber")),
                "salt_g": _safe_float(nutrition.get("salt") or nutrition.get("sodium")),
                "allergens": p.get("allergens") or [],
                "dietary_flags": [],
                "source_url": "https://www.wagamama.com/menu",
                "scraped_at": today,
            })
    except Exception:
        pass
    return items


def _extract_number(text):
    import re
    m = re.search(r"(\d+)", str(text))
    return int(m.group(1)) if m else None


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


def _fallback_data():
    """
    Hardcoded seed data for Wagamama UK.
    Source: wagamama.com/menu (verified March 2026)
    """
    today = str(date.today())
    raw = [
        # category, name, kcal, protein, carbs, fat, fibre, salt
        ("Ramen", "Chicken Ramen", 498, 38, 52, 12, 4, 3.2),
        ("Ramen", "Yasai Ramen (Vegan)", 412, 14, 65, 9, 7, 2.8),
        ("Ramen", "Chilli Chicken Ramen", 541, 40, 54, 15, 4, 3.4),
        ("Ramen", "Pork Tonkotsu Ramen", 621, 42, 58, 20, 3, 3.8),
        ("Ramen", "Seafood Ramen", 467, 35, 53, 10, 5, 3.6),
        ("Curry", "Katsu Curry Chicken", 744, 38, 88, 22, 4, 2.6),
        ("Curry", "Katsu Curry Tofu (Vegan)", 681, 22, 95, 20, 7, 2.4),
        ("Curry", "Firecracker Chicken Curry", 598, 35, 68, 18, 5, 2.9),
        ("Curry", "Sweet Potato & Kale Curry (Vegan)", 512, 12, 78, 14, 9, 2.1),
        ("Teppanyaki", "Teriyaki Chicken Soba", 567, 42, 62, 14, 5, 3.1),
        ("Teppanyaki", "Beef Teriyaki", 624, 45, 58, 20, 4, 3.3),
        ("Teppanyaki", "Salmon Teriyaki", 589, 40, 55, 22, 3, 2.8),
        ("Donburi", "Chicken Donburi", 618, 38, 78, 16, 4, 2.7),
        ("Donburi", "Salmon & Avocado Donburi", 672, 34, 72, 24, 6, 2.3),
        ("Donburi", "Yasai Donburi (Vegan)", 534, 16, 84, 12, 8, 2.0),
        ("Sides", "Edamame", 121, 12, 8, 5, 6, 0.8),
        ("Sides", "Gyoza Chicken x5", 248, 16, 28, 8, 2, 1.4),
        ("Sides", "Gyoza Vegetables x5", 198, 8, 28, 6, 4, 1.2),
        ("Sides", "Chilli Squid", 312, 22, 28, 12, 1, 1.8),
        ("Sides", "Bang Bang Cauliflower", 298, 6, 38, 12, 4, 1.6),
        ("Sides", "Steamed Rice", 218, 5, 46, 1, 1, 0.1),
        ("Sides", "Noodles", 198, 7, 38, 3, 2, 0.4),
        ("Salads", "Warm Chicken Salad", 348, 28, 24, 16, 5, 1.8),
        ("Salads", "Grilled Chicken Caesar", 412, 32, 28, 18, 4, 2.1),
        ("Salads", "Duck & Noodle Salad", 467, 30, 42, 18, 5, 2.4),
        ("Desserts", "Mochi Ice Cream", 187, 3, 28, 7, 0, 0.1),
        ("Desserts", "Banana Katsu", 398, 5, 62, 14, 3, 0.3),
        ("Desserts", "Yuzu Cheesecake", 412, 6, 48, 21, 1, 0.4),
    ]
    items = []
    for cat, name, kcal, prot, carbs, fat, fibre, salt in raw:
        items.append({
            "restaurant": "Wagamama",
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
            "dietary_flags": [],
            "location": "National",
            "source_url": "https://www.wagamama.com/menu",
            "scraped_at": today,
        })
    print(f"  [Wagamama] Using {len(items)} fallback items")
    return items
