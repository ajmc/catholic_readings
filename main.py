from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import date, timedelta
import json

app = FastAPI()

BASE_DIR = Path(__file__).parent

@app.get("/")
def get_index():
    return FileResponse(BASE_DIR / "static" / "index.html")

#Serve the static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# -----------------------------
# Load Ordo
# -----------------------------
ORDO_PATH = Path("ordo_data") / "ordo_2025.json"
with open(ORDO_PATH, "r", encoding="utf-8") as f:
    ordo_entries = json.load(f)

# -----------------------------
# Helper: Load Bible JSON
# -----------------------------
def load_bible(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_verse(bible, book_name, chapter_num, verse_num):
    for book in bible["books"]:
        if book["name"].lower() == book_name.lower():
            chapter = next((c for c in book["chapters"] if c["chapter"] == chapter_num), None)
            if chapter:
                verse = next((v for v in chapter["verses"] if v["verse"] == verse_num), None)
                if verse:
                    return verse["text"]
    return None

# -----------------------------
# Load Bibles
# -----------------------------
BASE_DIR = Path(__file__).parent
DRC_PATH = BASE_DIR / "bible_data" / "formats" / "json" / "DRC.json"
VULGATE_PATH = BASE_DIR / "bible_data" / "formats" / "json" / "Vulgate.json"
VULG_CLEMENTINE_PATH = BASE_DIR / "bible_data" / "formats" / "json" / "VulgClementine.json"

drc_bible = load_bible(DRC_PATH)
vulgate_bible = load_bible(VULGATE_PATH)
vulg_clementine_bible = load_bible(VULG_CLEMENTINE_PATH)

# -----------------------------
# Ordo endpoints
# -----------------------------
# -----------------------------
# Helper: Ordo lookup by date
# -----------------------------
def get_entries_for_date(date_str: str):
    """
    Returns the ordo entries for a given date string (YYYY-MM-DD).
    Accepts either the romcal dict (date -> [entries]) or a list of entries
    where each entry has a 'date' field.
    """
    # validate date format
    try:
        _ = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD")

    # romcal as dict (fast lookup)
    if isinstance(ordo_entries, dict):
        return ordo_entries.get(date_str, [])

    # romcal as list (fallback)
    if isinstance(ordo_entries, list):
        return [entry for entry in ordo_entries if entry.get("date") == date_str]

    # unexpected format
    return []

# -----------------------------
# Ordo endpoints
# -----------------------------
@app.get("/ordo/today")
def get_ordo_today():
    """Return ordo entries for today (YYYY-MM-DD)"""
    today_str = date.today().isoformat()
    return get_entries_for_date(today_str)

@app.get("/ordo/{date_str}")
def get_ordo_by_date(date_str: str):
    """Return ordo entries for a specific date (YYYY-MM-DD)"""
    return get_entries_for_date(date_str)

@app.get("/ordo/previous/{date_str}")
def get_ordo_previous(date_str: str):
    """
    Return ordo entries for the previous day relative to date_str.
    Example: /ordo/previous/2025-09-20 -> entries for 2025-09-19
    """
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD")

    prev_date = (d - timedelta(days=1)).isoformat()
    return get_entries_for_date(prev_date)

@app.get("/ordo/next/{date_str}")
def get_ordo_next(date_str: str):
    """
    Return ordo entries for the next day relative to date_str.
    Example: /ordo/next/2025-09-20 -> entries for 2025-09-21
    """
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD")

    next_date = (d + timedelta(days=1)).isoformat()
    return get_entries_for_date(next_date)

# -----------------------------
# Readings endpoints
# -----------------------------
@app.get("/readings/today")
def get_readings_today():
    today_str = date.today().isoformat()
    # Corrected: ordo_entries is a dict keyed by date
    todays_ordo_entries = ordo_entries.get(today_str, [])

    readings_today = []
    for entry in todays_ordo_entries:
        citations = entry.get("citations", [])
        entry_readings = []
        for citation in citations:
            try:
                book, chapter_verse = citation.split(maxsplit=1)  # e.g., "Genesis 1:1"
                chapter_num, verse_num = map(int, chapter_verse.split(":"))
                text_drc = get_verse(drc_bible, book, chapter_num, verse_num)
                text_vulgate = get_verse(vulgate_bible, book, chapter_num, verse_num)
                text_clementine = get_verse(vulg_clementine_bible, book, chapter_num, verse_num)
                entry_readings.append({
                    "citation": citation,
                    "DRC": text_drc,
                    "Vulgate": text_vulgate,
                    "VulgClementine": text_clementine   
                })
            except Exception:  
                continue

        readings_today.append({
            "date": today_str,
            "ordo_entry": entry,
            "readings": entry_readings
        })

    return readings_today

