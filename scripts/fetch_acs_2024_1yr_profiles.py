#!/usr/bin/env python3
"""Fetch compact keyless ACS 2024 1-year profiles for states, districts, counties, places, and PUMAs."""

from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/"
TABLES = {
    "b01001": ("age_sex", "B01001", {"B01001_E001", "B01001_M001", "B01001_E002", "B01001_E026"}),
    "b15003": ("education", "B15003", {"B15003_E001", "B15003_M001", "B15003_E002", "B15003_E017", "B15003_E025"}),
    "b17001": ("poverty", "B17001", {"B17001_E001", "B17001_M001", "B17001_E002", "B17001_E017"}),
    "b19013": ("income", "B19013", {"B19013_E001", "B19013_M001"}),
    "b25001": ("housing", "B25001", {"B25001_E001", "B25001_M001"}),
    "b02001": ("race", "B02001", {"B02001_E001", "B02001_M001", "B02001_E002", "B02001_E003", "B02001_E004", "B02001_E005", "B02001_E006", "B02001_E007", "B02001_E008"}),
}
GEO = {
    "state": (b"0400000US", 2, "state_geoid", "state", "state_name"),
    "district": (b"5001900US", 4, "district_geoid", "district", "district_name"),
    "county": (b"0500000US", 5, "county_geoid", "county", "county_name"),
    "place": (b"1600000US", 7, "place_geoid", "place", "place_name"),
    "puma": (b"795P200US", 7, "puma_geoid", "puma", "puma_name"),
}

def fetch(geo_kind, table, label, table_label, fields, names, retrieved_at):
    prefix, length, geoid_key, stem, name_key = GEO[geo_kind]
    source = BASE + f"acsdt1y2024-{table}.dat"
    rows = []
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        for line in response:
            if not line.startswith(prefix):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            raw = dict(zip(header, values))
            geoid = raw["GEO_ID"][-length:]
            row = {key: (int(value) if value.lstrip("-").isdigit() else value) for key, value in raw.items() if key == "GEO_ID" or key in fields}
            row.update({geoid_key: geoid, "state_fips": geoid[:2], "state_name": names.get(geoid[:2]), "source": source, "table": table_label, "vintage": "2024 ACS 1-year", "retrieved_at": retrieved_at})
            if name_key != "state_name":
                row[name_key] = names.get(geoid)
            rows.append(row)
    rows.sort(key=lambda row: row["GEO_ID"])
    filename = f"acs_{stem}_{label}_2024.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return source, filename, len(rows)

def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    names = {row["state_fips"]: row["name"] for row in json.loads((NORMALIZED / "states.json").read_text(encoding="utf-8"))}
    names.update({row["GEOID"]: row["NAME"] for row in json.loads((NORMALIZED / "counties_2023.json").read_text(encoding="utf-8"))})
    names.update({row["GEOID"]: row["NAME"] for row in json.loads((NORMALIZED / "places_2023.json").read_text(encoding="utf-8"))})
    results = {}
    for geo_kind in GEO:
        for table, (label, table_label, fields) in TABLES.items():
            source, filename, count = fetch(geo_kind, table, label, table_label, fields, names, retrieved_at)
            results[filename] = {"source": source, "records": count, "file": "data/normalized/" + filename}
    manifest = {"retrieved_at": retrieved_at, "tables": results, "note": "Public table-based ACS 2024 1-year summary files; compact state, congressional-district, eligible county/place, and PUMA fields; no API key used."}
    (RAW / "acs_2024_1yr_profiles_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
