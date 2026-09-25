#!/usr/bin/env python3
"""Fetch keyless ACS 2023 5-year county-subdivision profile tables."""

from datetime import datetime, timezone
import csv, json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/"
TABLES = {
    "b01001": ("acs_cousub_age_sex_2023.json", "B01001"),
    "b19013": ("acs_cousub_income_2023.json", "B19013"),
    "b17001": ("acs_cousub_poverty_2023.json", "B17001"),
    "b15003": ("acs_cousub_education_2023.json", "B15003"),
    "b25001": ("acs_cousub_housing_2023.json", "B25001"),
    "b02001": ("acs_cousub_race_2023.json", "B02001"),
}
KEEP_FIELDS = {
    "B01001": {"B01001_E001", "B01001_M001", "B01001_E002", "B01001_E026"},
    "B19013": {"B19013_E001", "B19013_M001"},
    "B17001": {"B17001_E001", "B17001_M001", "B17001_E002", "B17001_E017"},
    "B15003": {"B15003_E001", "B15003_M001", "B15003_E002", "B15003_E017", "B15003_E025"},
    "B25001": {"B25001_E001", "B25001_M001"},
    "B02001": {"B02001_E001", "B02001_M001", "B02001_E002", "B02001_E003", "B02001_E004", "B02001_E005", "B02001_E006", "B02001_E007", "B02001_E008"},
}


def fetch_table(table, output_name, label, names):
    source = BASE + "acsdt5y2023-" + table + ".dat"
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        rows = []
        for line in response:
            if not line.startswith(b"0600000US"):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            row = dict(zip(header, values))
            geoid = row["GEO_ID"][-10:]
            state_fips = geoid[:2]
            row = {key: (int(value) if value.lstrip("-").isdigit() else value) for key, value in row.items() if key in KEEP_FIELDS[label] or key == "GEO_ID"}
            row.update({"county_subdivision_geoid": geoid, "state_fips": state_fips, "state_name": names.get(state_fips), "source": source, "table": label, "vintage": "2023 ACS 5-year"})
            rows.append(row)
    rows.sort(key=lambda row: row["GEO_ID"])
    (NORMALIZED / output_name).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return source, len(rows)


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    names = {row["state_fips"]: row["name"] for row in json.loads((NORMALIZED / "states.json").read_text())}
    results = {}
    for table, (output_name, label) in TABLES.items():
        source, count = fetch_table(table, output_name, label, names)
        results[label] = {"source": source, "file": "data/normalized/" + output_name, "records": count}
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "tables": results, "note": "Public table-based ACS 5-year summary files; no API key used."}
    (RAW / "acs_cousub_profiles_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
