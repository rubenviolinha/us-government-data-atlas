#!/usr/bin/env python3
"""Fetch keyless ACS 2023 5-year place profile tables from public files."""

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
    "b01001": ("acs_place_age_sex_2023.json", "B01001"),
    "b19013": ("acs_place_income_2023.json", "B19013"),
    "b25001": ("acs_place_housing_2023.json", "B25001"),
    "b02001": ("acs_place_race_2023.json", "B02001"),
}


def fetch_table(table, output_name, label, names):
    source = BASE + "acsdt5y2023-" + table + ".dat"
    request = Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=300) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        rows = []
        for line in response:
            if not line.startswith(b"1600000US"):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            row = dict(zip(header, values))
            geoid = row["GEO_ID"][-7:]
            state_fips = geoid[:2]
            row = {key: (int(value) if value.lstrip("-").isdigit() else value) for key, value in row.items()}
            row.update({"place_fips": geoid, "state_fips": state_fips, "state_name": names.get(state_fips), "source": source, "table": label})
            rows.append(row)
    rows.sort(key=lambda row: row["GEO_ID"])
    (NORMALIZED / output_name).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return source, len(rows)


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    names = {row["state_fips"]: row["name"] for row in json.loads((NORMALIZED / "states.json").read_text())}
    results = {}
    for table, (output_name, label) in TABLES.items():
        source, count = fetch_table(table, output_name, label, names)
        results[label] = {"source": source, "file": "data/normalized/" + output_name, "records": count}
    manifest = {"retrieved_at": retrieved_at, "tables": results, "note": "Public table-based ACS summary files; no API key used."}
    (RAW / "acs_place_profiles_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
