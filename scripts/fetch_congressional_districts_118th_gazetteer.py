#!/usr/bin/env python3
"""Fetch Census 118th Congress (2023) congressional district geography."""

from datetime import datetime, timezone
import csv, io, json, zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"; NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_118CDs_national.zip"


def main():
    payload = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300).read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        text = io.TextIOWrapper(archive.open(archive.namelist()[0]), encoding="utf-8-sig")
        rows = [{key.strip(): value.strip() for key, value in row.items() if key} for row in csv.DictReader(text, delimiter="\t")]
    for row in rows: row["congress"] = "118"
    rows.sort(key=lambda row: row["GEOID"])
    NORMALIZED.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    filename = "congressional_districts_118th_2023.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": URL, "format": "Census Gazetteer ZIP/TXT", "records": len(rows), "file": "data/normalized/" + filename, "note": "118th Congress congressional district geography; no API key used."}
    (RAW / "congressional_districts_118th_2023_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
