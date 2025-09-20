#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import os

BASE_URL = "https://catholic-resources.org/Lectionary"
SUNDAYS_URL = f"{BASE_URL}/Index-Sundays.htm"
WEEKDAYS_URL = f"{BASE_URL}/Index-Weekdays.htm"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36"
    )
}

def fetch_url(url: str) -> str:
    print(f"Fetching {url} ...")
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.text

def parse_index_page(html: str):
    """Extract citations (just text) from an index page."""
    soup = BeautifulSoup(html, "html.parser")
    citations = []

    # Felix Just’s index pages usually have <li> with references
    for li in soup.find_all("li"):
        text = li.get_text(strip=True)
        if text:
            citations.append(text)

    return citations

def main():
    print("Fetching Sunday citations...")
    sunday_html = fetch_url(SUNDAYS_URL)
    sunday_citations = parse_index_page(sunday_html)

    print("Fetching Weekday citations...")
    weekday_html = fetch_url(WEEKDAYS_URL)
    weekday_citations = parse_index_page(weekday_html)

    data = {
        "sundays": sunday_citations,
        "weekdays": weekday_citations,
    }

    os.makedirs("citations", exist_ok=True)
    with open("citations/felix_citations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Saved citations/felix_citations.json")

if __name__ == "__main__":
    main()

