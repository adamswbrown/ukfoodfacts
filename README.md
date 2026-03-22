# GlobalFoodFacts — Restaurant Calorie Explorer

Scrapes and catalogues nutrition data from restaurant chains across the UK, Australia, and New Zealand. Browse, search, filter, and compare meals via a web UI.

**Live app:** Deployed on Vercel (auto-deploys on push)

## What's in the database

- **2,700+ menu items** across 150+ restaurants in 3 countries
- **UK & Ireland** — Nando's, McDonald's, Wagamama, KFC, Greggs, Five Guys, Subway, Domino's, Boojum, Apache Pizza, Supermac's, Tim Hortons, and many more
- **Australia** — Hungry Jack's, Guzman y Gomez, Betty's Burgers, Roll'd, and more
- **New Zealand** — McDonald's NZ, Burger King NZ, BurgerFuel, and more
- **Local NI restaurants** — Bangor and Belfast independents
- **Custom meals** — add your own items via the UI

Every item includes: calories, protein, carbs, fat, fibre, salt, allergens, dietary flags, category, and source URL.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium  # only needed for Wagamama scraper
```

## Usage

```bash
# Scrape all data and build the JSON database
python main.py

# Start the web UI on http://localhost:5050
python app.py
```

## Web UI features

- Search across all restaurants, dishes, and locations
- Filter by restaurant, location (National / Bangor / Belfast / etc.), and category
- Sort by any column (calories, protein, etc.)
- Colour-coded calories: green (<400), amber (400-699), red (700+)
- Detail modal with full macro breakdown
- Add custom meals with location tagging
- Delete custom meals

## Data schema

```json
{
  "restaurant": "Chain Name",
  "category": "Category",
  "item": "Dish Name",
  "description": "",
  "location": "National",
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

## Project structure

```
├── main.py                 # Entry point — runs all scrapers, writes JSON
├── app.py                  # Flask server + embedded HTML/JS UI
├── scrapers/
│   ├── nandos.py           # Live scraper + fallback data
│   ├── mcdonalds.py        # Live scraper + fallback data
│   ├── wagamama.py         # Playwright scraper + fallback data
│   ├── uk_chains.py        # 70 national chains (fallback data)
│   ├── local_ni.py         # 17 local NI restaurants (estimated data)
│   ├── custom.py           # User-added custom meals
│   └── __init__.py
├── output/
│   ├── nutrition_db.json   # Combined database (rebuilt on each scrape)
│   └── custom_items.json   # User-added items (persists across scrapes)
├── api/
│   └── index.py            # Vercel serverless entry point
├── vercel.json             # Vercel deployment config
├── .github/
│   └── workflows/
│       └── scrape.yml      # Daily auto-scrape via GitHub Actions
└── requirements.txt
```

## Scheduling & auto-updates

The nutrition database is automatically refreshed via **GitHub Actions**.

### Schedule

| What | When | Workflow |
|------|------|----------|
| **Daily scrape** | Every day at **06:15 UTC** (07:15 BST) | `scrape.yml` |
| **Meal approval** | When you close a `meal-submission` issue | `approve-meal.yml` |
| **Meal deletion** | Manual trigger from Actions tab | `delete-meal.yml` |

All three workflows commit changes to the repo, which triggers a **Vercel redeploy** automatically.

### How the daily scrape works

1. GitHub Actions cron fires at **06:15 UTC** daily (see `.github/workflows/scrape.yml`)
2. Spins up a Linux VM, installs Python 3.12, dependencies, and Playwright Chromium
3. Runs `python main.py` — executes all scrapers including the Playwright-based Wagamama scraper
4. If `output/nutrition_db.json` changed, commits and pushes the update
5. The push triggers a **Vercel redeploy** — the live site gets fresh data automatically
6. If nothing changed (same data), no commit is made — keeps git history clean

### How meal submissions work

1. A user clicks **"+ Add a Meal"** on the site and fills in the form
2. The app creates a **GitHub Issue** with the `meal-submission` label (requires `GITHUB_TOKEN` env var)
3. You review the issue on GitHub — it has a formatted table of the nutrition data
4. **To approve**: close the issue. The `approve-meal.yml` workflow parses the data, adds it to the database, commits, and Vercel redeploys
5. **To reject**: remove the `meal-submission` label, then close (or just ignore it)

### How to delete a meal

1. Go to **Actions** > **Delete Meal** > **Run workflow**
2. Enter the exact restaurant name and dish name
3. The workflow removes it from both `nutrition_db.json` and `custom_items.json`, commits, and Vercel redeploys
4. Only repo collaborators can trigger this — no keys or passwords needed

### Manual scrape trigger

You can trigger a full re-scrape anytime:
1. Go to **Actions** > **Scrape Nutrition Data**
2. Click **Run workflow** > **Run workflow**

### Why GitHub Actions (not Vercel Cron)?

- The Wagamama scraper needs **Playwright + headless Chromium** (~200MB), which can't run in Vercel's serverless environment (50MB bundle limit, 10s timeout on Hobby)
- GitHub Actions provides a full Linux VM with no size constraints
- Playwright browser binaries are cached between runs for speed
- It's **free** for public repos (unlimited minutes) or ~100-150 min/month for private repos (well within the 2,000 free minutes on GitHub Free)

### Required setup

**GitHub repo settings** (Settings > Actions > General):
- Under **Workflow permissions**, select **"Read and write permissions"**

**Vercel environment variables** (Settings > Environment Variables):
- `GITHUB_TOKEN` — a GitHub PAT with `repo` scope (allows the app to create issues)
- `ADMIN_KEY` — protects the DELETE API endpoint (set to something unguessable)

### Vercel deployment

The app is deployed as a Python serverless function on Vercel:
- **Viewing data**: Works normally (reads bundled JSON)
- **Submitting meals**: Creates a GitHub Issue for review
- **Refresh button**: Disabled on Vercel (returns 501) since scrapers can't run serverless
- Data freshness is maintained by the daily GitHub Actions cron

## Adding a new restaurant

### National chain (in uk_chains.py)

1. Add a `_YOUR_CHAIN` list with items in the format `(category, name, kcal, protein, carbs, fat, fibre, salt)`
2. Add it to `_ALL_CHAINS` at the bottom of the file
3. Run `python main.py` to rebuild

### Local restaurant (in local_ni.py)

1. Add a `_YOUR_RESTAURANT` list with the same item format
2. Add it to `_ALL_LOCAL` with `(name, location, source_url, items_list)`
3. The `location` field should be the town/city (e.g. "Bangor, NI", "Belfast")

### Via the site

Click **"+ Add a Meal"** on the live site. The submission creates a GitHub Issue for review — once approved, it's added to the database automatically.

## Scraper strategies

| Site type | Approach | Example |
|-----------|----------|---------|
| Static HTML / Next.js | `requests` + `__NEXT_DATA__` JSON extraction | Nando's |
| Internal JSON API | `requests` + direct API call | McDonald's |
| JS-rendered (React/Vue) | Playwright with network interception | Wagamama |
| No live scraping | Hardcoded fallback data | UK Chains, Local NI |

## Notes

- Be polite: scrapers add a 1s delay between chains
- Fallback data is used when live scraping fails
- Local NI restaurant data is estimated based on typical portion sizes
- For personal/hobby use only — do not redistribute the data commercially
