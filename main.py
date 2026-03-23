"""
GlobalFoodFacts — main runner
Runs all configured scrapers, deduplicates, logs results, and saves unified JSON output.
"""

import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import nandos, mcdonalds, wagamama, uk_chains, uk_pubs, uk_restaurants, local_ni, custom, burgerking_nz, rolld_au, mcdonalds_nz, burgerfuel_nz, bettys_burgers, hungryjacks, gyg_au, grilld_au, lotf_au

OUTPUT_FILE = Path(__file__).parent / "output" / "nutrition_db.json"
LOG_DIR = Path(__file__).parent / "output" / "logs"


def dedup_key(item):
    """Unique key for an item — restaurant + item name (case-insensitive)."""
    return (item["restaurant"].strip().lower(), item["item"].strip().lower())


def _strip_volatile_fields(items):
    """Return a comparable representation of items, ignoring fields that change every run."""
    return sorted(
        [{k: v for k, v in item.items() if k != "scraped_at"} for item in items],
        key=lambda x: (x.get("restaurant", ""), x.get("item", "")),
    )


def load_existing():
    """Load the current database for comparison."""
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            return json.load(f)
    return []


def run_all():
    start_time = datetime.now(timezone.utc)
    print("=" * 60)
    print(f"GlobalFoodFacts — {start_time.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # Load existing data for comparison
    existing = load_existing()
    existing_keys = {dedup_key(item) for item in existing}
    existing_restaurants = {item["restaurant"] for item in existing}
    print(f"Existing database: {len(existing)} items, {len(existing_restaurants)} restaurants")

    # Run scrapers
    all_items = []
    scraper_results = []
    scrapers = [
        ("Nandos", nandos.scrape),
        ("McDonalds", mcdonalds.scrape),
        ("Wagamama", wagamama.scrape),
        ("UK Chains", uk_chains.scrape),
        ("UK Pubs", uk_pubs.scrape),
        ("UK Restaurants", uk_restaurants.scrape),
        ("Local NI", local_ni.scrape),
        ("Custom", custom.scrape),
        ("Burger King NZ", burgerking_nz.scrape),
        ("Roll'd AU", rolld_au.scrape),
        ("McDonalds NZ", mcdonalds_nz.scrape),
        ("BurgerFuel NZ", burgerfuel_nz.scrape),
        ("Betty's Burgers", bettys_burgers.scrape),
        ("Hungry Jacks", hungryjacks.scrape),
        ("GYG AU", gyg_au.scrape),
        ("Grill'd AU", grilld_au.scrape),
        ("Lord of the Fries AU", lotf_au.scrape),
    ]

    for name, fn in scrapers:
        print(f"\n--- {name} ---")
        scraper_start = time.time()
        try:
            items = fn()
            elapsed = round(time.time() - scraper_start, 1)
            restaurants_in_scraper = set(item["restaurant"] for item in items)
            print(f"  OK: {len(items)} items from {len(restaurants_in_scraper)} restaurants ({elapsed}s)")
            scraper_results.append({
                "scraper": name,
                "status": "success",
                "items": len(items),
                "restaurants": len(restaurants_in_scraper),
                "elapsed_seconds": elapsed,
                "error": None,
            })
            all_items.extend(items)
            time.sleep(1)  # polite delay between scrapers
        except Exception as e:
            elapsed = round(time.time() - scraper_start, 1)
            print(f"  FAILED: {e} ({elapsed}s)")
            scraper_results.append({
                "scraper": name,
                "status": "failed",
                "items": 0,
                "restaurants": 0,
                "elapsed_seconds": elapsed,
                "error": str(e),
            })

    # Deduplicate — keep first occurrence (scrapers earlier in list take priority)
    seen = set()
    deduped = []
    duplicates_removed = 0
    for item in all_items:
        key = dedup_key(item)
        if key in seen:
            duplicates_removed += 1
            continue
        seen.add(key)
        deduped.append(item)

    # Calculate diffs vs existing database
    new_keys = seen - existing_keys
    removed_keys = existing_keys - seen
    new_restaurants = {item["restaurant"] for item in deduped} - existing_restaurants
    all_restaurants = {item["restaurant"] for item in deduped}

    new_items = [item for item in deduped if dedup_key(item) in new_keys]
    removed_items_count = len(removed_keys)

    # Build report
    end_time = datetime.now(timezone.utc)
    total_elapsed = round((end_time - start_time).total_seconds(), 1)

    report = {
        "timestamp": start_time.isoformat(),
        "duration_seconds": total_elapsed,
        "summary": {
            "total_items": len(deduped),
            "total_restaurants": len(all_restaurants),
            "previous_items": len(existing),
            "previous_restaurants": len(existing_restaurants),
            "new_items": len(new_items),
            "removed_items": removed_items_count,
            "duplicates_removed": duplicates_removed,
            "new_restaurants": list(new_restaurants),
            "net_change": len(deduped) - len(existing),
        },
        "scrapers": scraper_results,
        "new_items_detail": [
            {
                "restaurant": item["restaurant"],
                "item": item["item"],
                "calories_kcal": item.get("calories_kcal"),
            }
            for item in new_items[:50]  # Cap at 50 to keep log manageable
        ],
    }

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"SCRAPE COMPLETE — {end_time.strftime('%Y-%m-%d %H:%M UTC')} ({total_elapsed}s)")
    print(f"{'=' * 60}")
    print(f"  Total items:        {len(deduped)} (was {len(existing)}, net {len(deduped) - len(existing):+d})")
    print(f"  Total restaurants:  {len(all_restaurants)} (was {len(existing_restaurants)})")
    print(f"  New items:          {len(new_items)}")
    print(f"  Removed items:      {removed_items_count}")
    print(f"  Duplicates removed: {duplicates_removed}")
    if new_restaurants:
        print(f"  New restaurants:    {', '.join(sorted(new_restaurants))}")
    if new_items:
        print(f"\n  New items added:")
        for item in new_items[:20]:
            print(f"    + {item['restaurant']}: {item['item']} ({item.get('calories_kcal', '?')} kcal)")
        if len(new_items) > 20:
            print(f"    ... and {len(new_items) - 20} more")

    # Print scraper status table
    print(f"\n  Scraper Status:")
    failed = [r for r in scraper_results if r["status"] == "failed"]
    for r in scraper_results:
        status = "OK" if r["status"] == "success" else "FAIL"
        print(f"    [{status}] {r['scraper']}: {r['items']} items, {r['elapsed_seconds']}s"
              + (f" — {r['error']}" if r["error"] else ""))

    if failed:
        print(f"\n  WARNING: {len(failed)} scraper(s) failed!")

    # Check if data actually changed (ignore scraped_at timestamps)
    data_changed = _strip_volatile_fields(deduped) != _strip_volatile_fields(existing)

    if data_changed:
        # Save database
        OUTPUT_FILE.parent.mkdir(exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(deduped, f, indent=2)
        print(f"\n  Database saved: {OUTPUT_FILE}")

        # Save log
        LOG_DIR.mkdir(exist_ok=True)
        log_filename = f"scrape-{start_time.strftime('%Y-%m-%d-%H%M')}.json"
        log_path = LOG_DIR / log_filename
        with open(log_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"  Log saved: {log_path}")
    else:
        print(f"\n  No data changes detected — skipping database and log write.")

    # Write GitHub Actions job summary (if running in CI and data changed)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path and data_changed:
        with open(summary_path, "a") as f:
            f.write(f"## Scrape Report — {start_time.strftime('%Y-%m-%d %H:%M UTC')}\n\n")
            f.write(f"| Metric | Value |\n|--------|-------|\n")
            f.write(f"| Total items | {len(deduped)} |\n")
            f.write(f"| Total restaurants | {len(all_restaurants)} |\n")
            f.write(f"| New items | {len(new_items)} |\n")
            f.write(f"| Removed items | {removed_items_count} |\n")
            f.write(f"| Duplicates removed | {duplicates_removed} |\n")
            f.write(f"| Duration | {total_elapsed}s |\n\n")

            if failed:
                f.write(f"### Failed Scrapers\n\n")
                for r in failed:
                    f.write(f"- **{r['scraper']}**: {r['error']}\n")
                f.write("\n")

            f.write(f"### Scraper Results\n\n")
            f.write(f"| Scraper | Status | Items | Time |\n")
            f.write(f"|---------|--------|-------|------|\n")
            for r in scraper_results:
                status = "OK" if r["status"] == "success" else "FAIL"
                f.write(f"| {r['scraper']} | {status} | {r['items']} | {r['elapsed_seconds']}s |\n")

            if new_items:
                f.write(f"\n### New Items ({len(new_items)})\n\n")
                for item in new_items[:20]:
                    f.write(f"- {item['restaurant']}: {item['item']} ({item.get('calories_kcal', '?')} kcal)\n")
                if len(new_items) > 20:
                    f.write(f"- ... and {len(new_items) - 20} more\n")

    return deduped


if __name__ == "__main__":
    run_all()
