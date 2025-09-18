from fastapi import FastAPI, HTTPException
from datetime import date
import json
from pathlib import Path

app = FastAPI()

ORDO_PATH = Path(__file__).parent / "ordo_data" / "ordo_2025.json"

with open(ORDO_PATH, "r", encoding="utf-8") as f:
    ordo_entries = json.load(f)  # dict keyed by date

@app.get("/ordo/today")
def get_ordo_today():
    today_str = date.today().isoformat()  # "YYYY-MM-DD"
    todays_entries = ordo_entries.get(today_str)
    if not todays_entries:
        raise HTTPException(status_code=404, detail="No feast data for today")
    return todays_entries  # already a list


