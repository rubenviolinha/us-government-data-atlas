#!/usr/bin/env python3
"""Fetch the Census 2020-place to 2010-place relationship file."""

from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/place/tab20_place20_place10_natl.txt"


def main():
    text = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300).read().decode("utf-8-sig")
    rows = [
        {key: value for key, value in row.items() if key and value}
        for row in csv.DictReader(text.splitlines(), delimiter="|")
        if row.get("GEOID_PLACE_20") and row.get("GEOID_PLACE_10")
    ]
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    filename = "place_vintage_relationships_2020_2010.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": URL,
        "format": "Census relationship TXT",
        "records": len(rows),
        "file": "data/normalized/" + filename,
        "note": "2020-to-2010 Census place relationships with area overlap fields; no API key used.",
    }
    (RAW / "place_vintage_relationships_2020_2010_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
