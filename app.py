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
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
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
    --accent-default: #7c6af5;
    --green: #3ecf8e;
    --amber: #f59e0b;
    --red: #ef4444;
    --radius: 10px;
  }

  html { scroll-behavior: smooth; }

  body {
    font-family: 'Syne', sans-serif;
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
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    text-align: right;
  }

  .header-btn {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
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
    font-family: 'Syne', sans-serif;
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
    font-family: 'DM Mono', monospace;
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
    font-family: 'Syne', sans-serif;
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
  .tab-count {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    opacity: 0.7;
  }

  /* ── Results info ── */
  .results-info {
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
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
    gap: 6px;
    white-space: nowrap;
  }
  .restaurant-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .dot-Nandos { background: var(--accent-nandos); }
  .dot-McDonalds { background: var(--accent-mcdonalds); }
  .dot-Wagamama { background: var(--accent-wagamama); }

  .cell-item { font-weight: 600; }
  .cell-category {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
  }

  .cal-badge {
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 24px;
  }
  .daily-bar-wrap { margin-bottom: 24px; }
  .daily-bar-label {
    display: flex;
    justify-content: space-between;
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
    font-size: 1.3rem;
    font-weight: 500;
    display: block;
    margin-bottom: 2px;
  }
  .macro-block-label {
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
  }
  .extra-row-label { color: var(--muted); }

  .source-link {
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
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
    font-family: 'Syne', sans-serif;
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
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: opacity 0.15s;
  }
  .form-submit:hover { opacity: 0.85; }
  .form-submit:disabled { opacity: 0.5; cursor: not-allowed; }
  .custom-badge {
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
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
    font-family: 'DM Mono', monospace;
    background: #1a2744;
    border: 1px solid #2a3a5c;
    color: #8bb4f0;
  }
  .region-tag.national {
    background: #1a3328;
    border-color: #2a5c3a;
    color: #4ade80;
  }

  /* Contribution banner */
  .contrib-banner {
    background: linear-gradient(135deg, #1a2744 0%, #1a3328 100%);
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
</style>
</head>
<body>

<header>
  <div class="logo">
    🍽 UK Eats <span>calorie explorer</span>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <div class="header-meta" id="header-meta"></div>
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
      <p><strong>Know a restaurant we're missing?</strong> Add meals from any UK restaurant or takeaway — submissions are reviewed before going live.</p>
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
    <select id="location-filter" onchange="applyFilters()">
      <option value="">All locations</option>
    </select>
    <select id="category-filter" onchange="applyFilters()">
      <option value="">All categories</option>
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

<div class="toast" id="toast"></div>

<script>
let allData = [];
let activeRestaurant = 'all';
let currentSort = { key: null, dir: 1 };

// Dynamic colours for all restaurants (hash-based)
const _fixedColors = { Nandos:'#e63a1e', McDonalds:'#ffbc0d', Wagamama:'#d42b2b' };
function restaurantColor(name) {
  if (_fixedColors[name]) return _fixedColors[name];
  let h = 0;
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h);
  return `hsl(${Math.abs(h) % 360}, 55%, 55%)`;
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

  const bars = [
    { label: 'Total Dishes', value: allData.length },
    { label: 'Restaurants', value: restaurants.length },
    { label: 'Locations', value: locations.length },
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
      <div class="stat-label">Regions Covered</div>
      <div class="region-tags">${locations.map(l =>
        `<span class="region-tag${l === 'National' ? ' national' : ''}">${l}</span>`
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

  // Apply location filter first to determine available restaurants and categories
  const loc = document.getElementById('location-filter').value;
  let locationFiltered = data;
  if (loc) locationFiltered = data.filter(d => (d.location || 'National') === loc);

  // Rebuild restaurant tabs and category filter based on location-filtered data
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
          <div class="restaurant-dot" style="background:${restaurantColor(d.restaurant)}"></div>
          ${d.restaurant}${d.custom ? '<span class="custom-badge">custom</span>' : ''}
        </div>
      </td>
      <td class="cell-category">${d.location || 'National'}</td>
      <td class="cell-item">${d.item}</td>
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
  document.getElementById('modal-subtitle').textContent =
    `${item.restaurant} · ${item.location || 'National'} · ${item.category}`;

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

    ${item.allergens?.length ? `<div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--muted);margin-top:8px">Allergens: ${item.allergens.join(', ')}</div>` : ''}
    ${item.dietary_flags?.length ? `<div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--green);margin-top:4px">${item.dietary_flags.join(' · ')}</div>` : ''}

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

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeAddModal(); }
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
