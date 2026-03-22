"""
PDF scraping utilities — shared helpers for downloading and extracting
table data from restaurant nutrition PDFs using pdfplumber.
"""

import io
import os
import tempfile
import requests
import pdfplumber


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HobbyNutritionBot/1.0; personal use)",
}


def download_pdf(url, timeout=30):
    """
    Download a PDF from a URL and return a pdfplumber.PDF object.
    Caller should close it when done (or use as context manager).
    """
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return pdfplumber.open(io.BytesIO(resp.content))


def extract_tables(pdf, pages=None, table_settings=None):
    """
    Extract all tables from a PDF (or specific pages).
    Returns a list of tables, where each table is a list of rows,
    and each row is a list of cell strings.

    Args:
        pdf: a pdfplumber.PDF object
        pages: optional list of 0-based page indices, or None for all pages
        table_settings: optional dict passed to pdfplumber's extract_tables()
    """
    all_tables = []
    page_list = pdf.pages if pages is None else [pdf.pages[i] for i in pages]

    for page in page_list:
        kwargs = {}
        if table_settings:
            kwargs["table_settings"] = table_settings
        tables = page.extract_tables(**kwargs)
        if tables:
            all_tables.extend(tables)

    return all_tables


def clean_cell(val):
    """Clean a single cell value: strip whitespace, normalise empty/None."""
    if val is None:
        return ""
    val = str(val).strip()
    # Collapse internal whitespace (pdfplumber sometimes inserts line breaks)
    val = " ".join(val.split())
    if val in ("", "-", "—", "–", "N/A", "n/a", "na", "NA"):
        return ""
    return val


def clean_row(row):
    """Clean all cells in a row."""
    return [clean_cell(c) for c in row]


def clean_table(table):
    """Clean all rows in a table. Drops fully empty rows."""
    cleaned = []
    for row in table:
        row = clean_row(row)
        if any(cell != "" for cell in row):
            cleaned.append(row)
    return cleaned


def safe_int(val):
    """Convert a value to int, returning None on failure."""
    if val is None or val == "":
        return None
    try:
        # Handle strings like "1,234" or "~500"
        cleaned = str(val).replace(",", "").replace("~", "").strip()
        return int(float(cleaned)) if cleaned else None
    except (ValueError, TypeError):
        return None


def safe_float(val):
    """Convert a value to float rounded to 1dp, returning None on failure."""
    if val is None or val == "":
        return None
    try:
        cleaned = str(val).replace(",", "").replace("~", "").strip()
        return round(float(cleaned), 1) if cleaned else None
    except (ValueError, TypeError):
        return None
