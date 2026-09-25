#!/usr/bin/env python3
"""Fetch the National Governors Association's historical governor index."""

from datetime import datetime, timezone
from html import unescape
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

SOURCE_URL = "https://www.nga.org/former-governors/search/"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    request = Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    raw_path = RAW / "governors-nga.html"
    raw_path.write_bytes(payload)

    soup = BeautifulSoup(payload, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("NGA governor index table was not found")

    rows = []
    for tr in table.select("tbody tr"):
        cells = tr.find_all("td")
        if len(cells) != 4:
            continue
        link = cells[0].find("a")
        display_name = " ".join(cells[0].get_text(" ", strip=True).split())
        name = re.sub(r"^Gov\.\s*", "", display_name).strip()
        state = " ".join(cells[1].get_text(" ", strip=True).split())
        party = " ".join(cells[3].get_text(" ", strip=True).split())
        term_text = " ".join(cells[2].stripped_strings)
        terms = []
        for start, end in re.findall(r"(\d{4})\s*-\s*(\d{4})", term_text):
            terms.append({"start_year": int(start), "end_year": int(end)})
        rows.append({
            "name": name,
            "state": state,
            "party": party,
            "terms": terms,
            "profile_url": link.get("href") if link else None,
            "source": SOURCE_URL,
        })

    rows.sort(key=lambda row: (row["state"], row["name"], json.dumps(row["terms"])))
    output = NORMALIZED / "governors_nga.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": SOURCE_URL,
        "raw_file": "data/raw/governors-nga.html",
        "file": "data/normalized/governors_nga.json",
        "governors": len(rows),
        "terms": sum(len(row["terms"]) for row in rows),
        "term_year_anomalies": sum(term["start_year"] > term["end_year"] for row in rows for term in row["terms"]),
    }
    (RAW / "governor_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
