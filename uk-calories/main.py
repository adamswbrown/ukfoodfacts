"""
UK Restaurant Calorie Scraper — main runner
Runs all configured scrapers and saves unified JSON output.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import nandos, mcdonalds, wagamama, uk_chains, custom

OUTPUT_FILE = Path(__file__).parent / "output" / "nutrition_db.json"


def run_all():
    print("=" * 50)
    print("UK Restaurant Calorie Scraper")
    print("=" * 50)

    all_items = []
    scrapers = [
        ("Nandos", nandos.scrape),
        ("McDonalds", mcdonalds.scrape),
        ("Wagamama", wagamama.scrape),
        ("UK Chains", uk_chains.scrape),
        ("Custom", custom.scrape),
    ]

    for name, fn in scrapers:
        print(f"\n[{name}]")
        try:
            items = fn()
            all_items.extend(items)
            time.sleep(1)  # polite delay between scrapers
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'=' * 50}")
    print(f"Total items collected: {len(all_items)}")

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_items, f, indent=2)

    print(f"Saved to: {OUTPUT_FILE}")
    return all_items


if __name__ == "__main__":
    run_all()
