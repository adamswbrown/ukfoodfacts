# CLAUDE.md

Context for AI assistants working on this codebase. Read this before making changes.

## What this project is

A hobby Python project that scrapes nutritional data from UK restaurant chains (Nandos, McDonald's UK, Wagamama) and serves it through a local Flask web UI. Personal use only. No database, no auth, no deployment target — just runs locally.

## Architecture in one paragraph

`main.py` is the entry point. It calls each scraper in `scrapers/`, collects a list of dicts, and writes them to `output/nutrition_db.json`. `app.py` is a Flask server that reads that JSON file and serves it via a `/api/data` endpoint and a single-page HTML UI baked into the Python as a string. The UI is vanilla JS — no framework, no build step. The refresh button in the UI calls `/api/refresh` which re-runs `main.py` as a subprocess.

## Key design decisions

**Fallback-first scrapers.** Each scraper has a `_fallback_data()` function with hardcoded seed data. Live scraping is always attempted first, but if it fails (site structure changed, network issue, blocked), the fallback runs silently and the app stays usable. Don't remove fallback data when updating scrapers.

**Flat JSON, not a database.** The dataset is small (~100–500 items). SQLite would be overkill. The JSON file is the source of truth — it gets overwritten on every scrape run.

**No build step.** The entire frontend (HTML, CSS, JS) lives as a multiline string in `app.py`. This is intentional — it keeps the project runnable with a single `python app.py` command, no npm, no bundler. Keep it that way unless the frontend grows significantly.

**Playwright for JS-heavy sites.** Wagamama's menu is React-rendered. The scraper uses Playwright's async API with network response interception to catch the JSON payload before it hits the DOM. This is fragile — Wagamama can change their API structure. If the Playwright scraper breaks, check the browser DevTools Network tab on `wagamama.com/menu` for the new JSON endpoint.

## Data schema

Every item across all restaurants must conform to this shape:

```python
{
    "restaurant": str,           # "Nandos" | "McDonalds" | "Wagamama"
    "category": str,             # e.g. "Chicken", "Sides", "Ramen"
    "item": str,                 # dish name
    "description": str,         # optional, can be ""
    "calories_kcal": int | None,
    "protein_g": float | None,
    "carbs_g": float | None,
    "fat_g": float | None,
    "fibre_g": float | None,
    "salt_g": float | None,
    "allergens": list[str],      # empty list if unknown
    "dietary_flags": list[str],  # e.g. ["vegan", "gluten_free"]
    "source_url": str,           # canonical nutrition page URL
    "scraped_at": str,           # ISO date "YYYY-MM-DD"
}
```

Never use `None` as a string — use Python `None` (JSON `null`). The UI handles nulls gracefully with a `—` display.

## Adding a new restaurant scraper

1. Create `scrapers/yourchain.py`
2. Implement `scrape() -> list[dict]` — must return items matching the schema above
3. Implement `_fallback_data() -> list[dict]` — hardcoded seed data, called on any scrape failure
4. Add `_safe_int()` and `_safe_float()` helpers (copy from an existing scraper)
5. Import and add to the `scrapers` list in `main.py`
6. Add the restaurant name to the dot colour mapping in `app.py` (search for `dot-Nandos`)

**Scraper strategy by site type:**

- Static HTML / Next.js — use `requests` + parse the `<script id="__NEXT_DATA__">` JSON tag with `re.search` + `json.loads`
- Internal JSON API — inspect Network tab in DevTools, find the XHR/fetch call, hit it directly with `requests`
- JS-rendered (React/Vue) — use `playwright` async API with `page.on("response", handler)` to intercept JSON payloads

## Frontend UI (in app.py)

The entire UI is the `HTML` multiline string in `app.py`. Key JS functions:

- `loadData()` — fetches `/api/data` on page load
- `applyFilters()` — re-renders table based on search/filter/sort state
- `renderTable(data)` — writes `<tr>` rows into `#table-body`
- `openModal(i, d)` — shows the full nutrition detail modal for a row
- `refreshData()` — POSTs to `/api/refresh`, then reloads data

The calorie colour coding: green = under 400 kcal, amber = 400–699, red = 700+. These thresholds are in `calClass()`.

Fonts are loaded from Google Fonts (Manrope + Source Code Pro). The UI will still work offline — fonts just won't load.

## Running locally

```bash
pip install -r requirements.txt
playwright install chromium  # only needed for Wagamama scraper
python main.py               # scrape and build the JSON database
python app.py                # start web UI on http://localhost:5050
```

## Common failure modes

**Scraper returns 0 items and falls back:** The restaurant changed their site structure. Check the scraper's print output for which step failed, then inspect the actual HTML/network response to find the new data location.

**Playwright times out on Wagamama:** Their site is slow. Try increasing the `timeout=30000` value in `_async_scrape()`. Also check if their JS bundle URL patterns have changed.

**`__NEXT_DATA__` path changed on Nandos:** The `page_props` dict traversal in `nandos.py` may need updating. Add a `print(list(page_props.keys()))` to find the new key name.

**Flask shows stale data after refresh:** The `/api/data` endpoint reads from disk on every request — there's no in-memory cache. If data looks stale, check that `main.py` actually wrote to `output/nutrition_db.json` (the subprocess call in `/api/refresh` could have failed silently).

## Scope boundaries

This is a personal hobby project. Do not add:
- User authentication
- A real database (SQLite, Postgres, etc.) — JSON is fine at this scale
- Docker / deployment config — it's local-only
- A JavaScript framework / build pipeline
- Any commercial data redistribution

Do feel free to add:
- More restaurant scrapers (same pattern)
- Additional filter/sort options to the UI
- A GitHub Actions cron to auto-refresh the JSON on a schedule
- A CSV export endpoint
- A meal builder that sums macros across multiple items
