#!/usr/bin/env python3
"""Fetch compact, keyless ACS 2023 5-year PUMA profiles."""

from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/"
TABLES = {
    "b01001": ("acs_puma_age_sex_2023_5yr.json", "B01001", {"B01001_E001", "B01001_M001", "B01001_E002", "B01001_E026"}),
    "b15003": ("acs_puma_education_2023_5yr.json", "B15003", {"B15003_E001", "B15003_M001", "B15003_E002", "B15003_E017", "B15003_E025"}),
    "b17001": ("acs_puma_poverty_2023_5yr.json", "B17001", {"B17001_E001", "B17001_M001", "B17001_E002", "B17001_E017"}),
    "b19013": ("acs_puma_income_2023_5yr.json", "B19013", {"B19013_E001", "B19013_M001"}),
    "b25001": ("acs_puma_housing_2023_5yr.json", "B25001", {"B25001_E001", "B25001_M001"}),
    "b02001": ("acs_puma_race_2023_5yr.json", "B02001", {"B02001_E001", "B02001_M001", "B02001_E002", "B02001_E003", "B02001_E004", "B02001_E005", "B02001_E006", "B02001_E007", "B02001_E008"}),
}

def fetch_table(table, output_name, label, names, retrieved_at, fields):
    source = BASE + "acsdt5y2023-" + table + ".dat"
    rows = []
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        for line in response:
            if not line.startswith(b"795P200US"):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            raw = dict(zip(header, values))
            geoid = raw["GEO_ID"][-7:]
            row = {key: (int(value) if value.lstrip("-").isdigit() else value) for key, value in raw.items() if key == "GEO_ID" or key in fields}
            row.update({"puma_geoid": geoid, "state_fips": geoid[:2], "state_name": names.get(geoid[:2]), "source": source, "table": label, "vintage": "2023 ACS 5-year", "retrieved_at": retrieved_at})
            rows.append(row)
    rows.sort(key=lambda row: row["GEO_ID"])
    (NORMALIZED / output_name).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return source, len(rows)

def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    names = {row["state_fips"]: row["name"] for row in json.loads((NORMALIZED / "states.json").read_text(encoding="utf-8"))}
    results = {}
    for table, (output_name, label, fields) in TABLES.items():
        source, count = fetch_table(table, output_name, label, names, retrieved_at, fields)
        results[label] = {"source": source, "file": "data/normalized/" + output_name, "records": count}
    manifest = {"retrieved_at": retrieved_at, "tables": results, "note": "Public table-based ACS 5-year summary files; compact PUMA fields; no API key used."}
    (RAW / "acs_puma_5yr_profiles_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
