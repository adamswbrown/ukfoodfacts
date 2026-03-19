"""
Vercel serverless entry point.
Wraps the Flask app from app.py for deployment on Vercel's Python runtime.

On Vercel, the filesystem is read-only except for /tmp. This module:
- Copies bundled data files to /tmp on cold start if they don't exist there
- Points the app's DB_PATH and custom.CUSTOM_DB at /tmp copies
- Disables the /api/refresh endpoint (no subprocess/Playwright on serverless)
- Enables custom item add/delete via /tmp (ephemeral — resets on cold start)
"""

import json
import shutil
import sys
from pathlib import Path

# Ensure project root is on sys.path so scrapers/ can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# --- Adapt file paths for Vercel's read-only filesystem ---
VERCEL = bool(__import__("os").environ.get("VERCEL"))

if VERCEL:
    TMP_OUTPUT = Path("/tmp/output")
    TMP_OUTPUT.mkdir(exist_ok=True)

    BUNDLED_DB = PROJECT_ROOT / "output" / "nutrition_db.json"
    BUNDLED_CUSTOM = PROJECT_ROOT / "output" / "custom_items.json"
    TMP_DB = TMP_OUTPUT / "nutrition_db.json"
    TMP_CUSTOM = TMP_OUTPUT / "custom_items.json"

    # Copy bundled data to /tmp on cold start (only if not already there)
    if not TMP_DB.exists() and BUNDLED_DB.exists():
        shutil.copy2(BUNDLED_DB, TMP_DB)
    if not TMP_CUSTOM.exists() and BUNDLED_CUSTOM.exists():
        shutil.copy2(BUNDLED_CUSTOM, TMP_CUSTOM)

    # Patch paths before importing app
    import scrapers.custom as custom_mod
    custom_mod.CUSTOM_DB = TMP_CUSTOM

# Now import the Flask app
from app import app, DB_PATH
import app as app_mod

if VERCEL:
    app_mod.DB_PATH = TMP_DB


# Override refresh endpoint to return a helpful message on Vercel
@app.route("/api/refresh", methods=["POST"])
def api_refresh_vercel():
    from flask import jsonify
    return jsonify({
        "ok": False,
        "error": "Live scraping is disabled on Vercel (no Playwright/subprocess). "
                 "Data was pre-scraped and bundled at deploy time."
    }), 501


# Vercel expects the WSGI app as `app`
# (already named `app` from the import)
