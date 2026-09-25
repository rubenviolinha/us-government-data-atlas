#!/usr/bin/env python3
"""Fetch current 2024 national Census Gazetteer geography snapshots."""

from datetime import datetime, timezone
import csv
import io
import json
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/"
FILES = {
    "counties": ("2024_Gaz_counties_national.zip", "counties_2024.json"),
    "zctas": ("2024_Gaz_zcta_national.zip", "zctas_2024.json"),
    "cbsa": ("2024_Gaz_cbsa_national.zip", "cbsa_geography_2024.json"),
    "places": ("2024_Gaz_place_national.zip", "places_2024.json"),
    "tracts": ("2024_Gaz_tracts_national.zip", "tracts_2024.json"),
}

def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    manifest = {"retrieved_at": retrieved_at, "files": []}
    for label, (archive_name, output_name) in FILES.items():
        source = BASE + archive_name
        payload = urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300).read()
        raw_name = "census_" + archive_name
        (RAW / raw_name).write_bytes(payload)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            text = io.TextIOWrapper(archive.open(archive.namelist()[0]), encoding="utf-8-sig")
            rows = [{key.strip(): value.strip() for key, value in row.items() if key} for row in csv.DictReader(text, delimiter="\t")]
        key = "GEOID" if label != "cbsa" else "GEOID"
        rows.sort(key=lambda row: row[key])
        (NORMALIZED / output_name).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        manifest["files"].append({"path": "data/normalized/" + output_name, "source": source, "records": len(rows), "raw": "data/raw/" + raw_name})
    (RAW / "gazetteer_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
