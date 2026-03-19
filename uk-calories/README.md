# 🍽 UK Eats — Restaurant Calorie Explorer

Scrapes nutrition data from UK restaurant chains and serves it via a simple web UI.

## Restaurants Covered
- **Nandos** — static HTML + __NEXT_DATA__ JSON extraction (fallback: 30 seeded items)
- **McDonald's** — internal JSON API endpoint (fallback: 30 seeded items)
- **Wagamama** — Playwright headless browser with network interception (fallback: 28 seeded items)

## Setup

```bash
pip install requests beautifulsoup4 playwright flask
playwright install chromium
```

## Run the scrapers

```bash
python main.py
```

Output saved to `output/nutrition_db.json`

## Run the web UI

```bash
python app.py
```

Then open http://localhost:5050

## Adding more restaurants

1. Create `scrapers/yourchain.py` with a `scrape()` function that returns a list of dicts
2. Each dict should follow this schema:
```json
{
  "restaurant": "Chain Name",
  "category": "Category",
  "item": "Dish Name",
  "description": "optional",
  "calories_kcal": 450,
  "protein_g": 30.0,
  "carbs_g": 45.0,
  "fat_g": 12.0,
  "fibre_g": 3.0,
  "salt_g": 1.8,
  "allergens": [],
  "dietary_flags": [],
  "source_url": "https://...",
  "scraped_at": "2026-03-19"
}
```
3. Import and add to `main.py`

## Notes
- Be polite: scrapers add a 1s delay between chains
- Fallback data is used when live scraping fails (sites change their structure)
- Re-run `main.py` monthly to keep data fresh
- For personal/hobby use only — do not redistribute the data commercially
