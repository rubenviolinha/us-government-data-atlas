#!/usr/bin/env python3
"""Extract headline ACS 2023 5-year profile fields for every ZCTA."""

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
    "median_household_income": ("b19013", "B19013_E001"),
    "housing_units": ("b25001", "B25001_E001"),
    "race_total": ("b02001", "B02001_E001"),
    "poverty_universe": ("b17001", "B17001_E001"),
    "education_universe": ("b15003", "B15003_E001"),
}


def value(raw):
    return int(raw) if raw and raw.lstrip("-").isdigit() else raw


def fetch(table, field):
    source = BASE + f"acsdt5y2023-{table}.dat"
    result = {}
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=600) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        indexes = {name: index for index, name in enumerate(header)}
        for line in response:
            if not line.startswith(b"860Z200US"):
                continue
            cells = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            zcta = cells[indexes["GEO_ID"]][-5:]
            result[zcta] = value(cells[indexes[field]])
    return source, result


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    profiles = {}
    sources = {}
    for output_field, (table, field) in TABLES.items():
        source, values = fetch(table, field)
        sources[output_field] = source
        for zcta, parsed in values.items():
            profiles.setdefault(zcta, {"zcta": zcta, "source_vintage": "ACS 2023 5-year"})[output_field] = parsed
    rows = sorted(profiles.values(), key=lambda row: row["zcta"])
    filename = "zcta_profiles_acs_2023.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "sources": sources, "records": len(rows), "file": "data/normalized/" + filename, "note": "Compact headline-field extraction; raw bulk files are streamed and not copied into the repository."}
    (RAW / "zcta_profiles_acs_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
