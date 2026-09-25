#!/usr/bin/env python3
"""Fetch the complete public 2025 Census National Gazetteer geography set."""

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
BASE = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/"
FILES = {
    "119CDs": "congressional_districts_119th_2025.json",
    "aiannh": "american_indian_alaska_native_areas_2025.json",
    "aiannhrt": "american_indian_alaska_native_reservations_2025.json",
    "cbsa": "cbsa_geography_2025.json",
    "counties": "counties_2025.json",
    "cousubs": "county_subdivisions_2025.json",
    "elsd": "elementary_school_districts_2025.json",
    "place": "places_2025.json",
    "scsd": "secondary_school_districts_2025.json",
    "sdadm": "school_administrative_districts_2025.json",
    "sldl": "state_legislative_districts_lower_2025.json",
    "sldu": "state_legislative_districts_upper_2025.json",
    "state": "states_2025.json",
    "tracts": "tracts_2025.json",
    "ua": "urban_areas_2025.json",
    "unsd": "unified_school_districts_2025.json",
    "zcta": "zctas_2025.json",
}

def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    manifest = {"retrieved_at": retrieved_at, "source_directory": BASE, "files": []}
    for stem, output_name in FILES.items():
        archive_name = f"2025_Gaz_{stem}_national.zip"
        source = BASE + archive_name
        payload = urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300).read()
        raw_name = "census_" + archive_name
        (RAW / raw_name).write_bytes(payload)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            text = io.TextIOWrapper(archive.open(archive.namelist()[0]), encoding="utf-8-sig")
            rows = [{key.strip(): value.strip() for key, value in row.items() if key} for row in csv.DictReader(text, delimiter="|")]
        rows.sort(key=lambda row: row.get("GEOID", ""))
        (NORMALIZED / output_name).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        manifest["files"].append({"path": "data/normalized/" + output_name, "source": source, "records": len(rows), "raw": "data/raw/" + raw_name})
    (RAW / "gazetteer_2025_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
