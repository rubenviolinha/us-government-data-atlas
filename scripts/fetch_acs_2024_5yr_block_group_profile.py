#!/usr/bin/env python3
"""Fetch a compact keyless ACS 2024 5-year block-group profile."""

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
    "b01001": ("B01001", {"B01001_E001", "B01001_M001", "B01001_E002", "B01001_E026"}),
    "b25001": ("B25001", {"B25001_E001", "B25001_M001"}),
}
PREFIX = "1500000US"
EXPECTED = 242297
PARTS = 4


def integer_or_text(value):
    return int(value) if value.lstrip("-").isdigit() else value


def fetch(table, fields, retrieved_at):
    source = BASE + f"acsdt5y2024-{table}.dat"
    rows = {}
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=900) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        for line in response:
            if not line.startswith(PREFIX.encode("ascii")):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            raw = dict(zip(header, values))
            geoid = raw["GEO_ID"][len(PREFIX):]
            rows[geoid] = {key: integer_or_text(value) for key, value in raw.items() if key in fields}
    if len(rows) != EXPECTED:
        raise RuntimeError(f"{table}: expected {EXPECTED}, got {len(rows)}")
    return source, rows


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    fetched = {table: fetch(table, fields, retrieved_at) for table, (_label, fields) in TABLES.items()}
    population = fetched["b01001"][1]
    housing = fetched["b25001"][1]
    rows = []
    for geoid in sorted(population):
        row = {"GEO_ID": PREFIX + geoid, "block_group_geoid": geoid}
        row.update(population[geoid])
        row.update(housing[geoid])
        row.update({"source_population": fetched["b01001"][0], "source_housing": fetched["b25001"][0], "vintage": "2024 ACS 5-year", "retrieved_at": retrieved_at})
        rows.append(row)
    files = []
    for index in range(PARTS):
        start = (len(rows) * index) // PARTS
        end = (len(rows) * (index + 1)) // PARTS
        filename = f"acs_block_group_population_housing_2024_5yr_part{index + 1}.json"
        (NORMALIZED / filename).write_text(json.dumps(rows[start:end], separators=(",", ":")) + "\n", encoding="utf-8")
        files.append({"file": "data/normalized/" + filename, "records": end - start})
    manifest = {"retrieved_at": retrieved_at, "sources": {table: source for table, (source, _rows) in fetched.items()}, "format": "Joined table-based ACS summary files", "records": len(rows), "files": files, "note": "Compact 2024 ACS 5-year population and housing profile for all Census block groups, split into four release parts; no API key used."}
    (RAW / "acs_block_group_profile_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
