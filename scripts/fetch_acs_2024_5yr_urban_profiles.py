#!/usr/bin/env python3
"""Fetch compact 2024 ACS 5-year urban-area profiles without an API key."""

from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/"
TABLES = {
    "b01001": ("age_sex", "B01001", {"B01001_E001", "B01001_M001", "B01001_E002", "B01001_E026"}),
    "b15003": ("education", "B15003", {"B15003_E001", "B15003_M001", "B15003_E002", "B15003_E017", "B15003_E025"}),
    "b17001": ("poverty", "B17001", {"B17001_E001", "B17001_M001", "B17001_E002", "B17001_E017"}),
    "b19013": ("income", "B19013", {"B19013_E001", "B19013_M001"}),
    "b25001": ("housing", "B25001", {"B25001_E001", "B25001_M001"}),
    "b02001": ("race", "B02001", {"B02001_E001", "B02001_M001", "B02001_E002", "B02001_E003", "B02001_E004", "B02001_E005", "B02001_E006", "B02001_E007", "B02001_E008"}),
}


def integer_or_text(value):
    return int(value) if value.lstrip("-").isdigit() else value


def fetch(table, label, fields, retrieved_at):
    source = BASE + f"acsdt5y2024-{table}.dat"
    rows = []
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=600) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        for line in response:
            if not line.startswith(b"2690000US"):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            raw = dict(zip(header, values))
            geoid = raw["GEO_ID"][-11:]
            row = {key: integer_or_text(value) for key, value in raw.items() if key == "GEO_ID" or key in fields}
            row.update({"urban_area_geoid": geoid, "source": source, "table": label, "vintage": "2024 ACS 5-year", "retrieved_at": retrieved_at})
            rows.append(row)
    rows.sort(key=lambda row: row["GEO_ID"])
    filename = f"acs_urban_{label.lower().replace('b01001', 'age_sex').replace('b15003', 'education').replace('b17001', 'poverty').replace('b19013', 'income').replace('b25001', 'housing').replace('b02001', 'race')}_2024_5yr.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    return source, filename, len(rows)


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    results = {}
    for table, (label, table_name, fields) in TABLES.items():
        source, filename, count = fetch(table, table_name, fields, retrieved_at)
        results[filename] = {"source": source, "file": "data/normalized/" + filename, "records": count}
    manifest = {"retrieved_at": retrieved_at, "tables": results, "note": "Public table-based ACS 2024 5-year urban-area profile extracts; compact fields; no API key used."}
    (RAW / "acs_urban_profiles_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
