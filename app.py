"""
Flask web UI for UK Restaurant Nutrition Database
"""

from flask import Flask, jsonify, render_template_string, request
import json
import os
import subprocess
import sys
from pathlib import Path
import requests as http_requests

sys.path.insert(0, str(Path(__file__).parent))
from scrapers import custom

app = Flask(__name__)

DB_PATH = Path(__file__).parent / "output" / "nutrition_db.json"


def load_db():
    if not DB_PATH.exists():
        return []
    with open(DB_PATH) as f:
        return json.load(f)


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UK Eats — Restaurant Calorie Explorer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0e0e10;
    --surface: #16161a;
    --surface2: #1e1e24;
    --border: #2a2a35;
    --text: #e8e8f0;
    --muted: #6b6b80;
    --accent-nandos: #e63a1e;
    --accent-mcdonalds: #ffbc0d;
    --accent-wagamama: #d42b2b;
    --accent-burgerkingnz: #ff8732;
    --accent-rolld: #c8102e;
    --accent-mcdonaldsnz: #ffbc0d;
    --accent-burgerfuelnz: #e31837;
    --accent-bettysburgers: #f5a623;
    --accent-hungryjacks: #d62518;
    --accent-gyg: #f7941d;
    --accent-default: #7c6af5;
    --green: #3ecf8e;
    --amber: #f59e0b;
    --red: #ef4444;
    --radius: 10px;
  }

  [data-theme="light"] {
    --bg: #f5f5f7;
    --surface: #ffffff;
    --surface2: #f0f0f3;
    --border: #d8d8e0;
    --text: #1a1a2e;
    --muted: #6b6b80;
  }

  html { scroll-behavior: smooth; }

  body {
    font-family: 'Manrope', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.5;
  }

  /* ── Header ── */
  header {
    border-bottom: 1px solid var(--border);
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    background: rgba(14,14,16,0.92);
    backdrop-filter: blur(12px);
    z-index: 100;
  }
  [data-theme="light"] header {
    background: rgba(245,245,247,0.92);
  }

  .logo {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .logo span { color: var(--muted); font-weight: 400; font-size: 0.85rem; }

  .header-meta {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    text-align: right;
  }

  .header-btn {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'Source Code Pro', monospace;
    font-size: 0.75rem;
    padding: 7px 14px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .header-btn:hover { background: var(--border); }
  .header-btn.loading { opacity: 0.6; pointer-events: none; }
  .header-btn.primary { background: var(--accent-default); border-color: var(--accent-default); }
  .header-btn.primary:hover { opacity: 0.85; }

  /* ── Layout ── */
  .container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 32px;
  }

  /* ── Stats bar ── */
  .stats-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 28px;
  }

  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
  }
  .stat-label {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
  }
  .stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1;
  }

  /* ── Controls ── */
  .controls {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    align-items: center;
  }

  .search-wrap {
    position: relative;
    flex: 1;
    min-width: 220px;
  }
  .search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--muted);
    font-size: 0.9rem;
    pointer-events: none;
  }
  input[type="search"], select {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
    font-family: 'Manrope', sans-serif;
    font-size: 0.9rem;
    padding: 10px 14px;
    outline: none;
    transition: border-color 0.15s;
    width: 100%;
  }
  input[type="search"] { padding-left: 38px; }
  input[type="search"]:focus, select:focus { border-color: var(--accent-default); }
  select { cursor: pointer; min-width: 160px; flex: 0; }

  .sort-btn {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--muted);
    font-family: 'Source Code Pro', monospace;
    font-size: 0.75rem;
    padding: 10px 14px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
  }
  .sort-btn.active {
    background: var(--surface2);
    color: var(--text);
    border-color: var(--accent-default);
  }
  .sort-btn:hover { color: var(--text); }

  /* ── Restaurant tabs ── */
  .restaurant-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }
  .tab {
    padding: 7px 16px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    font-family: 'Manrope', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .tab:hover { color: var(--text); border-color: var(--muted); }
  .tab.active { color: var(--text); border-color: var(--text); background: var(--surface); }
  .tab[data-restaurant="Nandos"].active { border-color: var(--accent-nandos); color: var(--accent-nandos); }
  .tab[data-restaurant="McDonalds"].active { border-color: var(--accent-mcdonalds); color: var(--accent-mcdonalds); }
  .tab[data-restaurant="Wagamama"].active { border-color: var(--accent-wagamama); color: var(--accent-wagamama); }
  .tab[data-restaurant="Burger King NZ"].active { border-color: var(--accent-burgerkingnz); color: var(--accent-burgerkingnz); }
  .tab[data-restaurant="Roll'd"].active { border-color: var(--accent-rolld); color: var(--accent-rolld); }
  .tab[data-restaurant="McDonalds NZ"].active { border-color: var(--accent-mcdonaldsnz); color: var(--accent-mcdonaldsnz); }
  .tab[data-restaurant="BurgerFuel NZ"].active { border-color: var(--accent-burgerfuelnz); color: var(--accent-burgerfuelnz); }
  .tab[data-restaurant="Betty's Burgers"].active { border-color: var(--accent-bettysburgers); color: var(--accent-bettysburgers); }
  .tab[data-restaurant="Hungry Jacks"].active { border-color: var(--accent-hungryjacks); color: var(--accent-hungryjacks); }
  .tab[data-restaurant="Guzman y Gomez"].active { border-color: var(--accent-gyg); color: var(--accent-gyg); }
  .tab-count {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.7rem;
    opacity: 0.7;
  }

  /* ── Results info ── */
  .results-info {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 14px;
  }

  /* ── Table ── */
  .table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
  }

  thead th {
    padding: 12px 16px;
    text-align: left;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--muted);
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
  }
  thead th:hover { color: var(--text); }
  thead th.sorted { color: var(--text); }
  thead th .sort-indicator { margin-left: 4px; opacity: 0.5; }

  tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.1s;
    cursor: pointer;
  }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: var(--surface2); }

  td {
    padding: 11px 16px;
    vertical-align: middle;
  }

  .cell-restaurant {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
  }
  .restaurant-logo {
    width: 22px;
    height: 22px;
    border-radius: 5px;
    flex-shrink: 0;
    object-fit: contain;
    background: var(--surface2);
  }
  .restaurant-logo-fallback {
    width: 22px;
    height: 22px;
    border-radius: 5px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    font-weight: 700;
    color: #fff;
  }
  .modal-logo {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    object-fit: contain;
    background: var(--surface2);
  }
  .modal-logo-fallback {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    color: #fff;
  }
  .modal-subtitle {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .cell-item { font-weight: 600; }
  .cell-category {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.72rem;
    color: var(--muted);
  }

  .cal-badge {
    font-family: 'Source Code Pro', monospace;
    font-weight: 500;
    font-size: 0.9rem;
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
  }
  .cal-low { background: rgba(62,207,142,0.12); color: var(--green); }
  .cal-mid { background: rgba(245,158,11,0.12); color: var(--amber); }
  .cal-high { background: rgba(239,68,68,0.12); color: var(--red); }

  .macro {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.8rem;
    color: var(--muted);
  }
  .macro b { color: var(--text); font-weight: 500; }

  /* ── Empty state ── */
  .empty {
    text-align: center;
    padding: 64px 32px;
    color: var(--muted);
  }
  .empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
  .empty-title { font-size: 1.1rem; font-weight: 700; color: var(--text); margin-bottom: 6px; }

  /* ── Modal ── */
  .modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.7);
    backdrop-filter: blur(4px);
    z-index: 200;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }
  [data-theme="light"] .modal-overlay {
    background: rgba(0,0,0,0.3);
  }
  .modal-overlay.open { display: flex; }
  .modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    max-width: 520px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    animation: modal-in 0.2s ease;
  }
  @keyframes modal-in {
    from { opacity: 0; transform: translateY(16px) scale(0.97); }
    to { opacity: 1; transform: none; }
  }
  .modal-header {
    padding: 24px 24px 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
  }
  .modal-title { font-size: 1.2rem; font-weight: 800; line-height: 1.3; }
  .modal-subtitle {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 4px;
  }
  .modal-close {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--muted);
    width: 32px;
    height: 32px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
  }
  .modal-close:hover { color: var(--text); }
  .modal-body { padding: 20px 24px 24px; }

  .calories-big {
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 4px;
  }
  .calories-label {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 24px;
  }
  .daily-bar-wrap { margin-bottom: 24px; }
  .daily-bar-label {
    display: flex;
    justify-content: space-between;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    margin-bottom: 6px;
  }
  .daily-bar {
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
  }
  .daily-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.4s ease;
  }

  .macros-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 20px;
  }
  .macro-block {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
  }
  .macro-block-val {
    font-family: 'Source Code Pro', monospace;
    font-size: 1.3rem;
    font-weight: 500;
    display: block;
    margin-bottom: 2px;
  }
  .macro-block-label {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .extras-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 16px;
  }
  .extra-row {
    display: flex;
    justify-content: space-between;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.78rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
  }
  .extra-row-label { color: var(--muted); }

  .source-link {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    text-decoration: none;
    display: block;
    margin-top: 12px;
  }
  .source-link:hover { color: var(--text); }

  /* ── Add modal form ── */
  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .form-grid .full { grid-column: 1 / -1; }
  .form-group label {
    display: block;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 5px;
  }
  .form-group input, .form-group select {
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 6px;
    font-family: 'Manrope', sans-serif;
    font-size: 0.85rem;
    padding: 8px 12px;
    outline: none;
    transition: border-color 0.15s;
  }
  .form-group input:focus { border-color: var(--accent-default); }
  .form-submit {
    margin-top: 16px;
    width: 100%;
    padding: 11px;
    border-radius: 8px;
    border: none;
    background: var(--accent-default);
    color: #fff;
    font-family: 'Manrope', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: opacity 0.15s;
  }
  .form-submit:hover { opacity: 0.85; }
  .form-submit:disabled { opacity: 0.5; cursor: not-allowed; }
  .custom-badge {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.6rem;
    background: var(--accent-default);
    color: #fff;
    padding: 1px 6px;
    border-radius: 3px;
    margin-left: 6px;
    vertical-align: middle;
  }

  /* ── Toast ── */
  .toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 18px;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.8rem;
    opacity: 0;
    transform: translateY(8px);
    transition: all 0.2s;
    z-index: 300;
    pointer-events: none;
  }
  .toast.show { opacity: 1; transform: none; }

  /* Region tags */
  .region-map { grid-column: 1 / -1; }
  .region-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 2px; }
  .region-tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Source Code Pro', monospace;
    background: #1a2744;
    border: 1px solid #2a3a5c;
    color: #8bb4f0;
  }
  .region-tag.national {
    background: #1a3328;
    border-color: #2a5c3a;
    color: #4ade80;
  }
  [data-theme="light"] .region-tag {
    background: #e0ecff;
    border-color: #b0c8f0;
    color: #2a5090;
  }
  [data-theme="light"] .region-tag.national {
    background: #d8f5e0;
    border-color: #90d8a0;
    color: #1a7030;
  }

  /* Contribution banner */
  .contrib-banner {
    background: linear-gradient(135deg, #1a2744 0%, #1a3328 100%);
  }
  [data-theme="light"] .contrib-banner {
    background: linear-gradient(135deg, #e0ecff 0%, #d8f5e0 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
  }
  .contrib-banner p {
    margin: 0;
    font-size: 0.85rem;
    color: var(--muted);
  }
  .contrib-banner strong { color: var(--text); }
  .contrib-banner .contrib-btn {
    padding: 7px 18px;
    border-radius: 6px;
    background: #4ade80;
    color: #0a0a0a;
    font-weight: 600;
    font-size: 0.8rem;
    border: none;
    cursor: pointer;
    white-space: nowrap;
  }
  .contrib-banner .contrib-btn:hover { background: #22c55e; }

  /* ── Request restaurant form ── */
  .request-form textarea {
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 6px;
    font-family: 'Manrope', sans-serif;
    font-size: 0.85rem;
    padding: 8px 12px;
    outline: none;
    resize: vertical;
    min-height: 60px;
    transition: border-color 0.15s;
  }
  .request-form textarea:focus { border-color: var(--accent-default); }

  /* ── Mobile responsive ── */
  @media (max-width: 768px) {
    header {
      padding: 12px 16px;
      flex-direction: column;
      gap: 10px;
      align-items: stretch;
    }
    header > div:last-child {
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 6px;
    }
    .logo { font-size: 1.15rem; }
    .logo span { font-size: 0.75rem; }
    .header-btn { padding: 6px 10px; font-size: 0.68rem; }

    .container { padding: 16px; }

    .stats-bar {
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin-bottom: 16px;
    }
    .stat-card { padding: 10px 14px; }
    .stat-value { font-size: 1.3rem; }
    .stat-label { font-size: 0.6rem; }

    .contrib-banner {
      flex-direction: column;
      padding: 12px 14px;
      gap: 10px;
      align-items: stretch;
    }
    .contrib-banner p { font-size: 0.78rem; }
    .contrib-banner .contrib-btn { text-align: center; }

    .controls {
      gap: 8px;
      margin-bottom: 16px;
    }
    .search-wrap { min-width: 100%; }
    select { min-width: 0; flex: 1 1 calc(50% - 4px); font-size: 0.8rem; }
    input[type="search"], select { padding: 9px 12px; font-size: 0.82rem; }

    .restaurant-tabs {
      flex-wrap: nowrap;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      margin-bottom: 12px;
      padding-bottom: 4px;
    }
    .restaurant-tabs::-webkit-scrollbar { display: none; }
    .tab { flex-shrink: 0; padding: 6px 12px; font-size: 0.75rem; }

    /* Table: hide location & macros on mobile, compact cells */
    thead th:nth-child(2), tbody td:nth-child(2),
    thead th:nth-child(6), tbody td:nth-child(6) { display: none; }
    thead th { padding: 8px 10px; font-size: 0.6rem; }
    td { padding: 8px 10px; font-size: 0.8rem; }
    .cell-item { font-size: 0.82rem; }
    .cell-category { font-size: 0.65rem; }
    .cal-badge { font-size: 0.78rem; padding: 2px 7px; }

    /* Modal */
    .modal-overlay { padding: 12px; }
    .modal { border-radius: 12px; }
    .modal-header { padding: 16px 16px 12px; }
    .modal-title { font-size: 1.05rem; }
    .modal-body { padding: 14px 16px 18px; }
    .calories-big { font-size: 2.5rem; }
    .macros-grid { gap: 6px; }
    .macro-block { padding: 10px 8px; }
    .macro-block-val { font-size: 1.1rem; }

    /* Forms */
    .form-grid { grid-template-columns: 1fr; }

    /* Toast */
    .toast { bottom: 12px; right: 12px; left: 12px; font-size: 0.75rem; }
  }

  /* Extra small (< 400px) */
  @media (max-width: 400px) {
    header > div:last-child .header-btn:not(.primary) span:not(#refresh-icon) {
      display: none;
    }
    .stats-bar { grid-template-columns: 1fr 1fr; }
    select { flex: 1 1 100%; }
    thead th:nth-child(4), tbody td:nth-child(4) { display: none; }
    .calories-big { font-size: 2rem; }
  }
</style>
</head>
<body>

<header>
  <div class="logo">
    🍽 UK Eats <span>calorie explorer</span>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <div class="header-meta" id="header-meta"></div>
    <button class="header-btn" id="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark mode">☀ Light</button>
    <button class="header-btn" onclick="openRequestModal()">Request Restaurant</button>
    <button class="header-btn primary" onclick="openAddModal()">+ Add Meal</button>
    <button class="header-btn" id="refresh-btn" onclick="refreshData()">
      <span id="refresh-icon">↺</span> Refresh
    </button>
  </div>
</header>

<div class="container">

  <!-- Stats -->
  <div class="stats-bar" id="stats-bar"></div>

  <!-- Contribution banner -->
  <div class="contrib-banner">
    <div>
      <p><strong>Know a restaurant we're missing?</strong> Add meals manually or <a href="#" onclick="openRequestModal();return false" style="color:#8bb4f0;text-decoration:underline">request a restaurant</a> to be scraped — both create a GitHub issue for review.</p>
      <p style="margin-top:6px;font-size:0.75rem;color:var(--muted);opacity:0.7">Data refreshes automatically every day at 06:15 UTC. Last update shown above.</p>
    </div>
    <button class="contrib-btn" onclick="openAddModal()">+ Add a Meal</button>
  </div>

  <!-- Controls -->
  <div class="controls">
    <div class="search-wrap">
      <span class="search-icon">⌕</span>
      <input type="search" id="search" placeholder="Search dishes..." oninput="applyFilters()">
    </div>
    <select id="country-filter" onchange="applyFilters()">
      <option value="">All countries</option>
    </select>
    <select id="location-filter" onchange="applyFilters()">
      <option value="">All locations</option>
    </select>
    <select id="category-filter" onchange="applyFilters()">
      <option value="">All categories</option>
    </select>
    <select id="diet-filter" onchange="applyFilters()">
      <option value="">All diets</option>
      <option value="vegan">Vegan</option>
      <option value="vegetarian">Vegetarian</option>
      <option value="gluten_free">Gluten free</option>
    </select>
    <select id="sort-by" onchange="applyFilters()">
      <option value="">Sort: Default</option>
      <option value="calories_asc">Calories ↑ Low first</option>
      <option value="calories_desc">Calories ↓ High first</option>
      <option value="protein_desc">Protein ↓ High first</option>
      <option value="name_asc">Name A–Z</option>
    </select>
  </div>

  <!-- Restaurant tabs -->
  <div class="restaurant-tabs" id="restaurant-tabs">
    <button class="tab active" data-restaurant="all" onclick="setRestaurant('all', this)">
      All restaurants <span class="tab-count" id="count-all"></span>
    </button>
  </div>

  <!-- Results -->
  <div class="results-info" id="results-info"></div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th onclick="sortBy('restaurant')">Restaurant <span class="sort-indicator">↕</span></th>
          <th onclick="sortBy('location')">Location <span class="sort-indicator">↕</span></th>
          <th onclick="sortBy('item')">Dish <span class="sort-indicator">↕</span></th>
          <th onclick="sortBy('category')">Category <span class="sort-indicator">↕</span></th>
          <th onclick="sortBy('calories_kcal')">Calories <span class="sort-indicator">↕</span></th>
          <th>Macros</th>
        </tr>
      </thead>
      <tbody id="table-body"></tbody>
    </table>
    <div class="empty" id="empty-state" style="display:none">
      <div class="empty-icon">🔍</div>
      <div class="empty-title">No dishes found</div>
      <div>Try a different search or filter</div>
    </div>
  </div>

</div>

<!-- Item modal -->
<div class="modal-overlay" id="modal" onclick="closeModal(event)">
  <div class="modal" id="modal-content">
    <div class="modal-header">
      <div>
        <div class="modal-title" id="modal-title"></div>
        <div class="modal-subtitle" id="modal-subtitle"></div>
      </div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>

<!-- Add meal modal -->
<div class="modal-overlay" id="add-modal" onclick="closeAddModal(event)">
  <div class="modal">
    <div class="modal-header">
      <div>
        <div class="modal-title">Add a Meal</div>
        <div class="modal-subtitle">manually add a restaurant dish</div>
      </div>
      <button class="modal-close" onclick="closeAddModal()">✕</button>
    </div>
    <div class="modal-body">
      <form id="add-form" onsubmit="submitAddForm(event)">
        <div class="form-grid">
          <div class="form-group full">
            <label>Restaurant *</label>
            <input type="text" id="add-restaurant" required placeholder="e.g. Greggs" list="restaurant-list">
            <datalist id="restaurant-list"></datalist>
          </div>
          <div class="form-group full">
            <label>Location</label>
            <input type="text" id="add-location" placeholder="e.g. Bangor, NI, Cardiff... (default: National)" list="location-list">
            <datalist id="location-list"></datalist>
          </div>
          <div class="form-group full">
            <label>Dish Name *</label>
            <input type="text" id="add-item" required placeholder="e.g. Sausage Roll">
          </div>
          <div class="form-group full">
            <label>Category *</label>
            <input type="text" id="add-category" required placeholder="e.g. Savoury, Burgers, Pizza...">
          </div>
          <div class="form-group">
            <label>Calories (kcal) *</label>
            <input type="number" id="add-calories" required min="0" placeholder="327">
          </div>
          <div class="form-group">
            <label>Protein (g)</label>
            <input type="number" id="add-protein" step="0.1" min="0" placeholder="8">
          </div>
          <div class="form-group">
            <label>Carbs (g)</label>
            <input type="number" id="add-carbs" step="0.1" min="0" placeholder="26">
          </div>
          <div class="form-group">
            <label>Fat (g)</label>
            <input type="number" id="add-fat" step="0.1" min="0" placeholder="21">
          </div>
          <div class="form-group">
            <label>Fibre (g)</label>
            <input type="number" id="add-fibre" step="0.1" min="0" placeholder="1">
          </div>
          <div class="form-group">
            <label>Salt (g)</label>
            <input type="number" id="add-salt" step="0.1" min="0" placeholder="1.2">
          </div>
          <div class="form-group full">
            <label>Description (optional)</label>
            <input type="text" id="add-description" placeholder="Short description...">
          </div>
        </div>
        <button type="submit" class="form-submit" id="add-submit">Add to Database</button>
      </form>
    </div>
  </div>
</div>

<!-- Request restaurant modal -->
<div class="modal-overlay" id="request-modal" onclick="closeRequestModal(event)">
  <div class="modal">
    <div class="modal-header">
      <div>
        <div class="modal-title">Request a Restaurant</div>
        <div class="modal-subtitle">don't see a restaurant? let us know</div>
      </div>
      <button class="modal-close" onclick="closeRequestModal()">✕</button>
    </div>
    <div class="modal-body">
      <p style="font-size:0.85rem;color:var(--muted);margin-bottom:16px;line-height:1.6">
        This creates a <strong style="color:var(--text)">GitHub issue</strong> on the project repo.
        A scraper won't be built automatically — the maintainer will review the request
        and add support when they can. Including a link to the restaurant's nutrition page
        helps speed things up.
      </p>
      <form id="request-form" class="request-form" onsubmit="submitRequestForm(event)">
        <div class="form-grid">
          <div class="form-group full">
            <label>Restaurant Name *</label>
            <input type="text" id="req-restaurant" required placeholder="e.g. Greggs, Pret A Manger, Five Guys...">
          </div>
          <div class="form-group full">
            <label>Nutrition Page URL (helps a lot!)</label>
            <input type="url" id="req-url" placeholder="https://www.example.com/nutrition">
          </div>
          <div class="form-group full">
            <label>Notes (optional)</label>
            <textarea id="req-notes" placeholder="Any extra context — e.g. which region, specific menu items you want..."></textarea>
          </div>
        </div>
        <button type="submit" class="form-submit" id="req-submit">Submit Request</button>
      </form>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let allData = [];
let activeRestaurant = 'all';
let currentSort = { key: null, dir: 1 };

// ── Country mapping ──────────────────────────────────────────────
const _restaurantCountry = {
  'McDonalds NZ':'New Zealand', 'Burger King NZ':'New Zealand', 'BurgerFuel NZ':'New Zealand',
  'Hungry Jacks':'Australia', "Roll'd":'Australia', "Betty's Burgers":'Australia',
  'Guzman y Gomez':'Australia',
};
function getCountry(restaurant) {
  if (_restaurantCountry[restaurant]) return _restaurantCountry[restaurant];
  return 'United Kingdom';
}

// Dynamic colours for all restaurants (hash-based)
const _fixedColors = { Nandos:'#e63a1e', McDonalds:'#ffbc0d', Wagamama:'#d42b2b', 'Burger King NZ':'#ff8732', "Roll'd":'#c8102e', 'McDonalds NZ':'#ffbc0d', 'BurgerFuel NZ':'#e31837', "Betty's Burgers":'#f5a623', 'Hungry Jacks':'#d62518', 'Guzman y Gomez':'#f7941d' };
function restaurantColor(name) {
  if (_fixedColors[name]) return _fixedColors[name];
  let h = 0;
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h);
  return `hsl(${Math.abs(h) % 360}, 55%, 55%)`;
}

// ── Restaurant logo resolution ────────────────────────────────────
const _domainMap = {
  "Nandos":"nandos.co.uk","McDonalds":"mcdonalds.co.uk","Wagamama":"wagamama.com",
  "KFC":"kfc.co.uk","Burger King":"burgerking.co.uk","Subway":"subway.com",
  "Pizza Hut":"pizzahut.co.uk","Dominos":"dominos.co.uk","Greggs":"greggs.co.uk",
  "Costa Coffee":"costa.co.uk","Pret A Manger":"pret.co.uk","Starbucks":"starbucks.co.uk",
  "Pizza Express":"pizzaexpress.com","Zizzi":"zizzi.co.uk","Prezzo":"prezzorestaurants.co.uk",
  "Five Guys":"fiveguys.co.uk","TGI Fridays":"tgifridays.co.uk",
  "Frankie & Bennys":"frankieandbennys.com","Harvester":"harvester.co.uk",
  "Toby Carvery":"tobycarvery.co.uk","Wetherspoons":"jdwetherspoon.com",
  "GBK":"gbk.co.uk","Leon":"leon.co","Itsu":"itsu.com","Yo! Sushi":"yosushi.com",
  "Honest Burgers":"honestburgers.co.uk","The Real Greek":"therealgreek.com",
  "Las Iguanas":"lasiguanas.co.uk","Bills":"bills-website.co.uk",
  "Bella Italia":"bellaitalia.co.uk","ASK Italian":"askitalian.co.uk",
  "Tortilla":"tortilla.co.uk","Wasabi":"wasabi.uk.com","Franco Manca":"francomanca.co.uk",
  "Dishoom":"dishoom.com","Slim Chickens":"slimchickens.co.uk","Wingstop":"wingstop.co.uk",
  "Popeyes":"popeyes.co.uk","Chipotle":"chipotle.co.uk","Taco Bell":"tacobell.co.uk",
  "Chicken Cottage":"chickencottage.com","Morleys":"morleys.com",
  "German Doner Kebab":"germandonerkebab.com","Wimpy":"wimpy.uk.com",
  "Harry Ramsdens":"harryramsdens.co.uk","Beefeater":"beefeater.co.uk",
  "Miller & Carter":"millerandcarter.co.uk","Cafe Rouge":"caferouge.com",
  "Chiquito":"chiquito.co.uk","Caffe Nero":"caffenero.com","Papa Johns":"papajohns.co.uk",
  "Burger King NZ":"burgerking.co.nz","Roll'd":"rolld.com.au","McDonalds NZ":"mcdonalds.co.nz","BurgerFuel NZ":"burgerfuel.com","Betty's Burgers":"bettysburgers.com.au","Hungry Jacks":"hungryjacks.com.au","Guzman y Gomez":"guzmanygomez.com.au",
  "Pepes Piri Piri":"pepes.co.uk","Chopstix":"chopstixnoodles.co.uk",
  "Kokoro":"kokoromaidstone.co.uk","Hungry Horse":"hungryhorse.co.uk",
  "Loungers":"thelounges.co.uk","Cote Brasserie":"cote.co.uk",
  "Giggling Squid":"gigglingsquid.com","Gails Bakery":"gails.com",
  "Wahaca":"wahaca.co.uk","Rosas Thai":"rosasthai.com","Boojum":"boojummex.com",
  "Apache Pizza":"apache.ie","Supermacs":"supermacs.ie","Tim Hortons":"timhortons.co.uk",
  "Chick-fil-A":"chick-fil-a.co.uk","Four Star Pizza":"fourstarpizza.co.uk",
  "Eddie Rockets":"eddierockets.ie","Mary Browns":"marybrowns.com",
  "Shake Shack":"shakeshack.co.uk","The Botanist":"thebotanist.uk.com",
  "Comptoir Libanais":"comptoirlibanais.com","Busaba":"busaba.com",
  "Turtle Bay":"turtlebay.co.uk","Mowgli Street Food":"mowglistreetfood.com",
  "Krispy Kreme":"krispykreme.co.uk","Daves Hot Chicken":"daveshotchicken.co.uk",
  "Banana Tree":"bananatree.co.uk","Barburrito":"barburrito.co.uk",
  "Carluccios":"carluccios.com","Fireaway Pizza":"fireaway.co.uk",
  "German Gymnasium":"germangymnasium.com","Absurd Bird":"absurdbird.com",
  "Yard Sale Pizza":"yardsalepizza.com","Flat Iron":"flatironsteak.co.uk",
  "Patty & Bun":"pattyandbun.co.uk","MEATliquor":"meatliquor.com",
  "Bone Daddies":"bonedaddies.com","Rosa's Thai Cafe":"rosasthai.com",
  "Ole & Steen":"oleandsteen.co.uk","Paul Bakery":"paul-uk.com",
  "EAT.":"eat.co.uk","Benugo":"benugo.com","Black Sheep Coffee":"blacksheepcoffee.com",
  "Pho":"phocafe.co.uk","Coco di Mama":"cocodimama.co.uk","Benitos Hat":"benitoshat.com",
  "Ping Pong":"pingpongdimsum.com","Inamo":"inamo-restaurant.com",
  "Patisserie Valerie":"patisserie-valerie.co.uk","Upper Crust":"uppercrust.co.uk",
  "Cornish Bakery":"thecornishbakery.com","Esquires Coffee":"esquirescoffee.co.uk",
  "Muffin Break":"muffinbreak.co.uk","The Breakfast Club":"thebreakfastclubcafes.com",
  "Birds Bakery":"birdsbakery.com",
  "Sizzling Pubs":"sizzlingpubs.co.uk","Chef & Brewer":"chefandbrewer.com",
  "Flaming Grill":"flaminggrill.co.uk","All Bar One":"allbarone.co.uk",
  "Ember Inns":"emberinns.co.uk","Stonehouse Pizza & Carvery":"stonehouserestaurants.co.uk",
  "Slug & Lettuce":"slugandlettuce.co.uk","O'Neill's":"oneills.co.uk",
  "Nicholson's":"nicholsonspubs.co.uk","Vintage Inns":"vintageinns.co.uk",
  "Browns":"browns-restaurants.co.uk","Brewers Fayre":"brewersfayre.co.uk",
  "Pitcher & Piano":"pitcherandpiano.com","Young's Pubs":"youngs.co.uk",
  "Fuller's":"fullers.co.uk",
  "Barge East":"bargeeast.com","Park Chinois":"parkchinois.com",
  "The Ivy":"the-ivy.co.uk","El Gato Negro":"elgatonegro.uk",
  "20 Stories":"20stories.co.uk","Hawksmoor Manchester":"thehawksmoor.com",
  "The Kitchin":"thekitchin.com","The Witchery":"thewitchery.com",
  "Hawksmoor Edinburgh":"thehawksmoor.com",
  "The Wilderness":"thewildernessrestaurant.co.uk",
  "Pasture Birmingham":"pasture-restaurant.com","Wilsons":"wilsonsrestaurant.co.uk",
  "The Coconut Tree":"thecoconuttree.com","The Gannet":"thegannetgla.com",
  "The Finnieston":"thefinniestonbar.com","Gorse":"gorserestaurant.co.uk",
  "The Potted Pig":"thepottedpig.com","Bavette":"bavette.co.uk",
  "Akasya":"akasyarestaurant.co.uk",
  "The Boat House":"boathousebangor.com","Donegans":"donegansrestaurant.co.uk",
  "Coq & Bull Brasserie":"clandeboyelodge.com",
  "The Frying Squad":"fryingsquad.com","Bangla":"banglabangor.co.uk",
  "OX":"oxbelfast.com","The Muddlers Club":"themuddlersclub.com",
  "Coppi":"coppi.co.uk","Tribal Burger":"tribalburger.com",
  "Mourne Seafood Bar":"mourneseafood.com","Yugo":"yugobelfast.com",
  "Little Wing Pizzeria":"littlewingpizzeria.com"
};

// Cache logo load results to avoid repeated failed requests
const _logoCache = {};

function getDomain(restaurant) {
  return _domainMap[restaurant] || null;
}

function onLogoError(img) {
  const domain = img.dataset.domain;
  const fallbackCls = img.dataset.fallbackCls;
  const color = img.dataset.color;
  const initial = img.dataset.initial;
  if (!img.dataset.triedGoogle) {
    // First failure (Apistemic) — try Google Favicon
    img.dataset.triedGoogle = '1';
    img.src = 'https://www.google.com/s2/favicons?domain=' + domain + '&sz=128';
  } else {
    // Both failed — replace with coloured letter initial
    const span = document.createElement('span');
    span.className = fallbackCls;
    span.style.background = color;
    span.textContent = initial;
    img.replaceWith(span);
  }
}

function logoHtml(restaurant, size) {
  const cls = size === 'modal' ? 'modal-logo' : 'restaurant-logo';
  const fallbackCls = size === 'modal' ? 'modal-logo-fallback' : 'restaurant-logo-fallback';
  const domain = getDomain(restaurant);
  const color = restaurantColor(restaurant);
  const initial = restaurant.charAt(0).toUpperCase();

  if (!domain) {
    return `<span class="${fallbackCls}" style="background:${color}">${initial}</span>`;
  }

  return `<img class="${cls}"
    src="https://logos-api.apistemic.com/domain:${domain}"
    data-domain="${domain}"
    data-fallback-cls="${fallbackCls}"
    data-color="${color}"
    data-initial="${initial}"
    onerror="onLogoError(this)"
    alt="${restaurant}"
    loading="lazy">`;
}

// ── Boot ──────────────────────────────────────────────────────────
async function loadData() {
  try {
    const res = await fetch('/api/data');
    allData = await res.json();
    init();
  } catch(e) {
    showToast('Failed to load data');
  }
}

function init() {
  buildStats();
  buildCountryFilter();
  buildRestaurantTabs();
  buildLocationFilter();
  buildCategoryFilter();
  applyFilters();
  document.getElementById('header-meta').textContent =
    allData.length ? `Last scraped: ${allData[0].scraped_at}` : '';
}

// ── Stats ─────────────────────────────────────────────────────────
function buildStats() {
  const cals = allData.map(d => d.calories_kcal).filter(Boolean);
  const avg = Math.round(cals.reduce((a,b)=>a+b,0)/cals.length);
  const min = Math.min(...cals);
  const max = Math.max(...cals);
  const restaurants = [...new Set(allData.map(d=>d.restaurant))];
  const locations = [...new Set(allData.map(d=>d.location || 'National'))];
  const countries = [...new Set(allData.map(d=>getCountry(d.restaurant)))].sort();

  const bars = [
    { label: 'Total Dishes', value: allData.length },
    { label: 'Restaurants', value: restaurants.length },
    { label: 'Countries', value: countries.length },
    { label: 'Avg Calories', value: avg + ' kcal' },
    { label: 'Lowest Cal', value: min + ' kcal' },
    { label: 'Highest Cal', value: max + ' kcal' },
  ];
  document.getElementById('stats-bar').innerHTML = bars.map(s => `
    <div class="stat-card">
      <div class="stat-label">${s.label}</div>
      <div class="stat-value">${s.value}</div>
    </div>`).join('') + `
    <div class="stat-card region-map">
      <div class="stat-label">Countries</div>
      <div class="region-tags">${countries.map(c =>
        `<span class="region-tag">${c}</span>`
      ).join('')}</div>
    </div>`;
}

// ── Restaurant tabs ────────────────────────────────────────────────
function buildRestaurantTabs(sourceData) {
  const dataset = sourceData || allData;
  const restaurants = [...new Set(dataset.map(d => d.restaurant))];
  const container = document.getElementById('restaurant-tabs');

  // Preserve active restaurant selection, reset if not in filtered set
  const prevActive = activeRestaurant;
  if (prevActive !== 'all' && !restaurants.includes(prevActive)) {
    activeRestaurant = 'all';
  }

  container.innerHTML = '';
  const allBtn = document.createElement('button');
  allBtn.className = 'tab' + (activeRestaurant === 'all' ? ' active' : '');
  allBtn.dataset.restaurant = 'all';
  allBtn.onclick = () => setRestaurant('all', allBtn);
  allBtn.innerHTML = `All restaurants <span class="tab-count">${dataset.length}</span>`;
  container.appendChild(allBtn);

  restaurants.forEach(r => {
    const count = dataset.filter(d => d.restaurant === r).length;
    const btn = document.createElement('button');
    btn.className = 'tab' + (activeRestaurant === r ? ' active' : '');
    btn.dataset.restaurant = r;
    btn.onclick = () => setRestaurant(r, btn);
    btn.innerHTML = `<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:${restaurantColor(r)}"></span> ${r} <span class="tab-count">${count}</span>`;
    container.appendChild(btn);
  });
}

function setRestaurant(r, el) {
  activeRestaurant = r;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  applyFilters();
}

// ── Country filter ─────────────────────────────────────────────────
function buildCountryFilter() {
  const countries = [...new Set(allData.map(d => getCountry(d.restaurant)))].sort();
  const sel = document.getElementById('country-filter');
  const current = sel.value;
  sel.innerHTML = '<option value="">All countries</option>' +
    countries.map(c => `<option value="${c}" ${c===current?'selected':''}>${c}</option>`).join('');
}

// ── Location filter ────────────────────────────────────────────────
function buildLocationFilter() {
  const locations = [...new Set(allData.map(d => d.location || 'National'))].sort();
  const sel = document.getElementById('location-filter');
  const current = sel.value;
  sel.innerHTML = '<option value="">All locations</option>' +
    locations.map(l => `<option value="${l}" ${l===current?'selected':''}>${l}</option>`).join('');
}

// ── Category filter ────────────────────────────────────────────────
function buildCategoryFilter(sourceData) {
  const dataset = sourceData || allData;
  const filtered = activeRestaurant === 'all'
    ? dataset
    : dataset.filter(d => d.restaurant === activeRestaurant);
  const cats = [...new Set(filtered.map(d => d.category))].sort();
  const sel = document.getElementById('category-filter');
  const current = sel.value;
  sel.innerHTML = '<option value="">All categories</option>' +
    cats.map(c => `<option value="${c}" ${c===current?'selected':''}>${c}</option>`).join('');
}

// ── Filters & sort ─────────────────────────────────────────────────
function applyFilters() {
  let data = [...allData];

  // Apply country filter first
  const country = document.getElementById('country-filter').value;
  if (country) data = data.filter(d => getCountry(d.restaurant) === country);

  // Apply location filter to determine available restaurants and categories
  const loc = document.getElementById('location-filter').value;
  let locationFiltered = data;
  if (loc) locationFiltered = data.filter(d => (d.location || 'National') === loc);

  // Rebuild restaurant tabs and category filter based on filtered data
  buildRestaurantTabs(locationFiltered);
  buildCategoryFilter(locationFiltered);

  // Now apply restaurant filter
  if (activeRestaurant !== 'all') {
    data = data.filter(d => d.restaurant === activeRestaurant);
  }

  const q = document.getElementById('search').value.toLowerCase().trim();
  if (q) {
    data = data.filter(d =>
      d.item.toLowerCase().includes(q) ||
      d.category.toLowerCase().includes(q) ||
      d.restaurant.toLowerCase().includes(q) ||
      (d.location || '').toLowerCase().includes(q)
    );
  }

  if (loc) data = data.filter(d => (d.location || 'National') === loc);

  const cat = document.getElementById('category-filter').value;
  if (cat) data = data.filter(d => d.category === cat);

  const diet = document.getElementById('diet-filter').value;
  if (diet) data = data.filter(d => (d.dietary_flags || []).includes(diet));

  const sort = document.getElementById('sort-by').value;
  if (sort === 'calories_asc') data.sort((a,b) => (a.calories_kcal||999) - (b.calories_kcal||999));
  if (sort === 'calories_desc') data.sort((a,b) => (b.calories_kcal||0) - (a.calories_kcal||0));
  if (sort === 'protein_desc') data.sort((a,b) => (b.protein_g||0) - (a.protein_g||0));
  if (sort === 'name_asc') data.sort((a,b) => a.item.localeCompare(b.item));

  if (currentSort.key) {
    data.sort((a,b) => {
      const av = a[currentSort.key] ?? '';
      const bv = b[currentSort.key] ?? '';
      return typeof av === 'number'
        ? (av - bv) * currentSort.dir
        : String(av).localeCompare(String(bv)) * currentSort.dir;
    });
  }

  renderTable(data);
}

function sortBy(key) {
  if (currentSort.key === key) {
    currentSort.dir *= -1;
  } else {
    currentSort = { key, dir: 1 };
  }
  document.getElementById('sort-by').value = '';
  applyFilters();
}

// ── Table render ───────────────────────────────────────────────────
function renderTable(data) {
  const tbody = document.getElementById('table-body');
  const empty = document.getElementById('empty-state');
  const info = document.getElementById('results-info');

  info.textContent = `${data.length} dish${data.length !== 1 ? 'es' : ''} shown`;

  if (!data.length) {
    tbody.innerHTML = '';
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';

  tbody.innerHTML = data.map((d, i) => `
    <tr onclick="openModal(${i}, ${JSON.stringify(d).replace(/"/g, '&quot;')})">
      <td>
        <div class="cell-restaurant">
          ${logoHtml(d.restaurant, 'table')}
          ${d.restaurant}${d.custom ? '<span class="custom-badge">custom</span>' : ''}
        </div>
      </td>
      <td class="cell-category">${d.location || 'National'}</td>
      <td class="cell-item">${d.item}${(d.dietary_flags||[]).length ? ' <span style="font-size:0.65rem;color:var(--green);opacity:0.85">' + d.dietary_flags.map(f=>f==='gluten_free'?'GF':f==='vegan'?'V':f==='vegetarian'?'VG':f).join(' · ') + '</span>' : ''}</td>
      <td class="cell-category">${d.category}</td>
      <td><span class="cal-badge ${calClass(d.calories_kcal)}">${d.calories_kcal ?? '—'} kcal</span></td>
      <td>
        <div class="macro">
          <b>${d.protein_g ?? '—'}g</b> prot &nbsp;
          <b>${d.carbs_g ?? '—'}g</b> carbs &nbsp;
          <b>${d.fat_g ?? '—'}g</b> fat
        </div>
      </td>
    </tr>`).join('');

  // Store data for modal access
  window._tableData = data;
}

function calClass(kcal) {
  if (!kcal) return '';
  if (kcal < 400) return 'cal-low';
  if (kcal < 700) return 'cal-mid';
  return 'cal-high';
}

// ── Modal ──────────────────────────────────────────────────────────
function openModal(i, d) {
  const item = window._tableData[i] || d;
  document.getElementById('modal-title').textContent = item.item;
  document.getElementById('modal-subtitle').innerHTML =
    `${logoHtml(item.restaurant, 'modal')} ${item.restaurant} · ${item.location || 'National'} · ${item.category}`;

  const pct = item.calories_kcal ? Math.min(100, Math.round(item.calories_kcal / 2000 * 100)) : 0;
  const barColor = item.calories_kcal < 400 ? '#3ecf8e' : item.calories_kcal < 700 ? '#f59e0b' : '#ef4444';

  const desc = item.description ? `<p style="color:var(--muted);font-size:0.85rem;margin-bottom:20px">${item.description}</p>` : '';

  document.getElementById('modal-body').innerHTML = `
    ${desc}
    <div class="calories-big" style="color:${barColor}">${item.calories_kcal ?? '—'}</div>
    <div class="calories-label">kcal per serving</div>

    <div class="daily-bar-wrap">
      <div class="daily-bar-label">
        <span>% of 2,000 kcal daily reference</span>
        <span>${pct}%</span>
      </div>
      <div class="daily-bar">
        <div class="daily-bar-fill" style="width:${pct}%;background:${barColor}"></div>
      </div>
    </div>

    <div class="macros-grid">
      <div class="macro-block">
        <span class="macro-block-val">${item.protein_g ?? '—'}g</span>
        <span class="macro-block-label">Protein</span>
      </div>
      <div class="macro-block">
        <span class="macro-block-val">${item.carbs_g ?? '—'}g</span>
        <span class="macro-block-label">Carbs</span>
      </div>
      <div class="macro-block">
        <span class="macro-block-val">${item.fat_g ?? '—'}g</span>
        <span class="macro-block-label">Fat</span>
      </div>
    </div>

    <div class="extras-grid">
      <div class="extra-row">
        <span class="extra-row-label">Fibre</span>
        <span>${item.fibre_g ?? '—'}g</span>
      </div>
      <div class="extra-row">
        <span class="extra-row-label">Salt</span>
        <span>${item.salt_g ?? '—'}g</span>
      </div>
    </div>

    ${item.allergens?.length ? `<div style="font-family:'Source Code Pro',monospace;font-size:0.72rem;color:var(--muted);margin-top:8px">Allergens: ${item.allergens.join(', ')}</div>` : ''}
    ${item.dietary_flags?.length ? `<div style="font-family:'Source Code Pro',monospace;font-size:0.72rem;color:var(--green);margin-top:4px">${item.dietary_flags.join(' · ')}</div>` : ''}

    <a class="source-link" href="${item.source_url}" target="_blank" rel="noopener">
      ↗ Source: ${item.source_url}
    </a>
  `;

  document.getElementById('modal').classList.add('open');
}

function closeModal(e) {
  if (!e || e.target === document.getElementById('modal')) {
    document.getElementById('modal').classList.remove('open');
  }
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// ── Refresh ────────────────────────────────────────────────────────
async function refreshData() {
  const btn = document.getElementById('refresh-btn');
  const icon = document.getElementById('refresh-icon');
  btn.classList.add('loading');
  icon.textContent = '…';
  showToast('Running scrapers — this may take 30s...');
  try {
    await fetch('/api/refresh', { method: 'POST' });
    await loadData();
    showToast('Data refreshed ✓');
  } catch(e) {
    showToast('Refresh failed');
  }
  btn.classList.remove('loading');
  icon.textContent = '↺';
}

function showToast(msg, html) {
  const t = document.getElementById('toast');
  if (html) { t.innerHTML = msg; } else { t.textContent = msg; }
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 5000);
}

// ── Add modal ─────────────────────────────────────────────────────────
function openAddModal() {
  // Populate restaurant datalist for autocomplete
  const rlist = document.getElementById('restaurant-list');
  const restaurants = [...new Set(allData.map(d => d.restaurant))].sort();
  rlist.innerHTML = restaurants.map(r => `<option value="${r}">`).join('');
  // Populate location datalist
  const llist = document.getElementById('location-list');
  const locations = [...new Set(allData.map(d => d.location || 'National'))].sort();
  llist.innerHTML = locations.map(l => `<option value="${l}">`).join('');
  document.getElementById('add-modal').classList.add('open');
}

function closeAddModal(e) {
  if (!e || e.target === document.getElementById('add-modal')) {
    document.getElementById('add-modal').classList.remove('open');
  }
}

async function submitAddForm(e) {
  e.preventDefault();
  const btn = document.getElementById('add-submit');
  btn.disabled = true;
  btn.textContent = 'Adding...';

  const payload = {
    restaurant: document.getElementById('add-restaurant').value,
    location: document.getElementById('add-location').value || 'National',
    category: document.getElementById('add-category').value,
    item: document.getElementById('add-item').value,
    calories_kcal: document.getElementById('add-calories').value,
    protein_g: document.getElementById('add-protein').value || null,
    carbs_g: document.getElementById('add-carbs').value || null,
    fat_g: document.getElementById('add-fat').value || null,
    fibre_g: document.getElementById('add-fibre').value || null,
    salt_g: document.getElementById('add-salt').value || null,
    description: document.getElementById('add-description').value,
  };

  try {
    const res = await fetch('/api/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (result.ok) {
      const msg = result.issue_url
        ? 'Meal submitted for review! <a href="' + result.issue_url + '" target="_blank" style="color:#4ade80;text-decoration:underline">Track on GitHub</a>'
        : 'Meal submitted for review!';
      showToast(msg, true);
      document.getElementById('add-form').reset();
      document.getElementById('add-modal').classList.remove('open');
    } else {
      showToast('Error: ' + (result.error || 'Unknown'));
    }
  } catch(err) {
    showToast('Failed to add meal');
  }
  btn.disabled = false;
  btn.textContent = 'Add to Database';
}

// ── Request restaurant modal ──────────────────────────────────────────
function openRequestModal() {
  document.getElementById('request-modal').classList.add('open');
}

function closeRequestModal(e) {
  if (!e || e.target === document.getElementById('request-modal')) {
    document.getElementById('request-modal').classList.remove('open');
  }
}

async function submitRequestForm(e) {
  e.preventDefault();
  const btn = document.getElementById('req-submit');
  btn.disabled = true;
  btn.textContent = 'Submitting...';

  const payload = {
    restaurant: document.getElementById('req-restaurant').value,
    url: document.getElementById('req-url').value || null,
    notes: document.getElementById('req-notes').value || null,
  };

  try {
    const res = await fetch('/api/scrape-request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (result.ok) {
      const msg = result.issue_url
        ? 'Request logged for review — <a href="' + result.issue_url + '" target="_blank" style="color:#4ade80;text-decoration:underline">track on GitHub</a>'
        : 'Request logged for review';
      showToast(msg, true);
      document.getElementById('request-form').reset();
      document.getElementById('request-modal').classList.remove('open');
    } else {
      showToast('Error: ' + (result.error || 'Unknown'));
    }
  } catch(err) {
    showToast('Failed to submit request');
  }
  btn.disabled = false;
  btn.textContent = 'Submit Request';
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeAddModal(); closeRequestModal(); }
});

// ── Theme toggle ──────────────────────────────────────────────────
function applyTheme(theme, save) {
  document.documentElement.setAttribute('data-theme', theme);
  if (save) localStorage.setItem('theme', theme);
  const btn = document.getElementById('theme-toggle');
  btn.textContent = theme === 'light' ? '\u263D Dark' : '\u2600 Light';
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark', true);
}

// Use saved preference, or follow system setting
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
  applyTheme(savedTheme, false);
} else {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(prefersDark ? 'dark' : 'light', false);
}
// Update theme when system preference changes (only if user hasn't manually chosen)
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (!localStorage.getItem('theme')) {
    applyTheme(e.matches ? 'dark' : 'light', false);
  }
});
loadData();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/data")
def api_data():
    data = load_db()
    # Optional filtering
    q = request.args.get("q", "").lower()
    restaurant = request.args.get("restaurant", "")
    category = request.args.get("category", "")

    if q:
        data = [d for d in data if q in d["item"].lower() or q in d["category"].lower()]
    if restaurant:
        data = [d for d in data if d["restaurant"] == restaurant]
    if category:
        data = [d for d in data if d["category"] == category]

    return jsonify(data)


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return jsonify({"ok": True, "output": result.stdout})
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Timeout"}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


ADMIN_KEY = os.environ.get("ADMIN_KEY", "ukfoodfacts2026")
API_KEY = os.environ.get("API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "adamswbrown/ukfoodfacts")


@app.route("/api/items", methods=["POST"])
def api_add_item():
    """Submit a meal via GitHub Issue or fall back to local pending queue."""
    data = request.get_json(force=True)
    required = ["restaurant", "category", "item", "calories_kcal"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    if not GITHUB_TOKEN:
        # Fall back to local pending queue when no GitHub token configured
        new_item = custom.submit_item(
            restaurant=data["restaurant"],
            category=data["category"],
            item_name=data["item"],
            calories_kcal=data["calories_kcal"],
            protein_g=data.get("protein_g"),
            carbs_g=data.get("carbs_g"),
            fat_g=data.get("fat_g"),
            fibre_g=data.get("fibre_g"),
            salt_g=data.get("salt_g"),
            description=data.get("description", ""),
            location=data.get("location", "National"),
        )
        return jsonify({"ok": True, "item": new_item, "status": "pending_local"})

    # Build GitHub Issue
    restaurant = data["restaurant"]
    item_name = data["item"]
    title = f"[Meal Submission] {restaurant} - {item_name}"

    body = f"""### Meal Submission

| Field | Value |
|-------|-------|
| Restaurant | {restaurant} |
| Location | {data.get('location', 'National')} |
| Category | {data['category']} |
| Item | {item_name} |
| Calories | {data['calories_kcal']} |
| Protein (g) | {data.get('protein_g', '')} |
| Carbs (g) | {data.get('carbs_g', '')} |
| Fat (g) | {data.get('fat_g', '')} |
| Fibre (g) | {data.get('fibre_g', '')} |
| Salt (g) | {data.get('salt_g', '')} |
| Description | {data.get('description', '')} |

```json
{json.dumps(data, indent=2)}
```"""

    try:
        resp = http_requests.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/issues",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={
                "title": title,
                "body": body,
                "labels": ["meal-submission"],
            },
            timeout=15,
        )
        resp.raise_for_status()
        issue = resp.json()
        return jsonify({
            "ok": True,
            "status": "submitted",
            "issue_url": issue["html_url"],
            "issue_number": issue["number"],
        })
    except Exception as exc:
        return jsonify({"ok": False, "error": f"GitHub API error: {str(exc)}"}), 502



SCRAPE_REQUESTS_PATH = Path(__file__).parent / "output" / "scrape_requests.json"


@app.route("/api/scrape-request", methods=["POST"])
def api_scrape_request():
    """Request a new restaurant to be scraped — creates a GitHub issue or logs locally."""
    data = request.get_json(force=True)
    restaurant = data.get("restaurant", "").strip()
    if not restaurant:
        return jsonify({"ok": False, "error": "Restaurant name is required"}), 400

    url = data.get("url", "").strip() or None
    notes = data.get("notes", "").strip() or None

    if not GITHUB_TOKEN:
        # Fall back to local JSON log
        requests_log = []
        if SCRAPE_REQUESTS_PATH.exists():
            with open(SCRAPE_REQUESTS_PATH) as f:
                requests_log = json.load(f)
        from datetime import date
        requests_log.append({
            "restaurant": restaurant,
            "url": url,
            "notes": notes,
            "requested_at": date.today().isoformat(),
            "status": "pending",
        })
        SCRAPE_REQUESTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SCRAPE_REQUESTS_PATH, "w") as f:
            json.dump(requests_log, f, indent=2)
        return jsonify({"ok": True, "status": "logged_locally"})

    # Build GitHub Issue
    title = f"[Scrape Request] {restaurant}"
    body_parts = [
        "### Restaurant Scrape Request\n",
        f"**Restaurant:** {restaurant}",
    ]
    if url:
        body_parts.append(f"**Nutrition page URL:** {url}")
    if notes:
        body_parts.append(f"**Notes:** {notes}")
    body_parts.append("\n---\n*Submitted via the UK Eats UI*")
    body = "\n".join(body_parts)

    try:
        resp = http_requests.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/issues",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={
                "title": title,
                "body": body,
                "labels": ["scrape-request"],
            },
            timeout=15,
        )
        resp.raise_for_status()
        issue = resp.json()
        return jsonify({
            "ok": True,
            "status": "submitted",
            "issue_url": issue["html_url"],
            "issue_number": issue["number"],
        })
    except Exception as exc:
        return jsonify({"ok": False, "error": f"GitHub API error: {str(exc)}"}), 502


@app.route("/api/items", methods=["DELETE"])
def api_delete_item():
    """Delete a custom item by restaurant + item name (requires admin key)."""
    data = request.get_json(force=True)
    if data.get("key") != ADMIN_KEY:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    restaurant = data.get("restaurant", "")
    item_name = data.get("item", "")
    if not restaurant or not item_name:
        return jsonify({"ok": False, "error": "restaurant and item required"}), 400

    deleted = custom.delete_item(restaurant, item_name)
    if not deleted:
        return jsonify({"ok": False, "error": "Item not found in custom entries"}), 404

    # Also remove from main DB
    db = load_db()
    db = [d for d in db if not (d["restaurant"] == restaurant and d["item"] == item_name)]
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

    return jsonify({"ok": True})


# ── Authenticated API (v1) ─────────────────────────────────────────


def _check_api_key():
    """Validate API key from header or query param."""
    if not API_KEY:
        return False, jsonify({"ok": False, "error": "API not configured"}), 503
    key = request.headers.get("X-API-Key") or request.args.get("api_key")
    if key != API_KEY:
        return False, jsonify({"ok": False, "error": "Invalid or missing API key"}), 401
    return True, None, None


@app.route("/api/v1/data")
def api_v1_data():
    """Full nutrition database — authenticated for external apps."""
    ok, err, code = _check_api_key()
    if not ok:
        return err, code
    db = load_db()
    # Support optional filters via query params
    restaurant = request.args.get("restaurant")
    location = request.args.get("location")
    category = request.args.get("category")
    search = request.args.get("q", "").lower()
    if restaurant:
        db = [d for d in db if d["restaurant"] == restaurant]
    if location:
        db = [d for d in db if d.get("location", "National") == location]
    if category:
        db = [d for d in db if d["category"] == category]
    if search:
        db = [d for d in db if search in d["item"].lower()
              or search in d["restaurant"].lower()
              or search in d.get("category", "").lower()]
    return jsonify({
        "ok": True,
        "count": len(db),
        "data": db,
    })


@app.route("/api/v1/restaurants")
def api_v1_restaurants():
    """List all restaurants with item counts — authenticated."""
    ok, err, code = _check_api_key()
    if not ok:
        return err, code
    db = load_db()
    restaurants = {}
    for d in db:
        name = d["restaurant"]
        if name not in restaurants:
            restaurants[name] = {"restaurant": name, "locations": set(), "count": 0}
        restaurants[name]["count"] += 1
        restaurants[name]["locations"].add(d.get("location", "National"))
    result = [{"restaurant": v["restaurant"], "locations": sorted(v["locations"]),
               "item_count": v["count"]} for v in restaurants.values()]
    return jsonify({"ok": True, "count": len(result), "data": result})


@app.route("/api/v1/locations")
def api_v1_locations():
    """List all locations with restaurant counts — authenticated."""
    ok, err, code = _check_api_key()
    if not ok:
        return err, code
    db = load_db()
    locations = {}
    for d in db:
        loc = d.get("location", "National")
        if loc not in locations:
            locations[loc] = {"location": loc, "restaurants": set(), "count": 0}
        locations[loc]["count"] += 1
        locations[loc]["restaurants"].add(d["restaurant"])
    result = [{"location": v["location"], "restaurants": sorted(v["restaurants"]),
               "item_count": v["count"]} for v in locations.values()]
    return jsonify({"ok": True, "count": len(result), "data": result})


@app.route("/api/v1/search")
def api_v1_search():
    """Search meals by name — authenticated."""
    ok, err, code = _check_api_key()
    if not ok:
        return err, code
    q = request.args.get("q", "").lower().strip()
    if not q:
        return jsonify({"ok": False, "error": "q parameter required"}), 400
    db = load_db()
    results = [d for d in db if q in d["item"].lower()
               or q in d["restaurant"].lower()]
    return jsonify({"ok": True, "count": len(results), "data": results})


if __name__ == "__main__":
    app.run(debug=True, port=5050)
