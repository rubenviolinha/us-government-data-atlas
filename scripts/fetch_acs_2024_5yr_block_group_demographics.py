#!/usr/bin/env python3
"""Fetch compact keyless ACS 2024 5-year block-group demographic profiles."""

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
    "b15003": ("education", {"B15003_E001", "B15003_M001", "B15003_E002", "B15003_E017", "B15003_E025"}),
    "b19013": ("income", {"B19013_E001", "B19013_M001"}),
    "b02001": ("race", {"B02001_E001", "B02001_M001", "B02001_E002", "B02001_E003", "B02001_E004", "B02001_E005", "B02001_E006", "B02001_E007", "B02001_E008"}),
    "b11001": ("households", {"B11001_E001", "B11001_M001", "B11001_E002"}),
    "b23025": ("labor", {"B23025_E001", "B23025_M001", "B23025_E002", "B23025_E005"}),
    "b25003": ("occupancy", {"B25003_E001", "B25003_M001", "B25003_E002", "B25003_E003"}),
}
PREFIX = "1500000US"
EXPECTED = 242297
PARTS = 4


def integer_or_text(value):
    return int(value) if value.lstrip("-").isdigit() else value


def fetch(table, fields):
    source = BASE + f"acsdt5y2024-{table}.dat"
    rows = []
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=900) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        for line in response:
            if not line.startswith(PREFIX.encode("ascii")):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            raw = dict(zip(header, values))
            geoid = raw["GEO_ID"][len(PREFIX):]
            row = {key: integer_or_text(value) for key, value in raw.items() if key == "GEO_ID" or key in fields}
            row["block_group_geoid"] = geoid
            rows.append(row)
    if len(rows) != EXPECTED:
        raise RuntimeError(f"{table}: expected {EXPECTED}, got {len(rows)}")
    rows.sort(key=lambda row: row["GEO_ID"])
    return source, rows


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    results = {}
    for table, (label, fields) in TABLES.items():
        source, rows = fetch(table, fields)
        files = []
        for index in range(PARTS):
            start = (len(rows) * index) // PARTS
            end = (len(rows) * (index + 1)) // PARTS
            filename = f"acs_block_group_{label}_2024_5yr_part{index + 1}.json"
            output = []
            for row in rows[start:end]:
                output.append({**row, "source": source, "table": table.upper(), "vintage": "2024 ACS 5-year", "retrieved_at": retrieved_at})
            (NORMALIZED / filename).write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
            files.append({"file": "data/normalized/" + filename, "records": len(output)})
        results[label] = {"source": source, "table": table.upper(), "records": len(rows), "files": files}
    manifest = {"retrieved_at": retrieved_at, "format": "Joined table-based ACS summary files", "tables": results, "omitted_tables": {"b17001": "Census publishes no B17001 poverty rows for block groups in the 2024 5-year table-based summary files."}, "note": "Compact 2024 ACS 5-year education, income, race, household, labor, and occupancy profiles for all Census block groups, split into four parts per table; no API key used."}
    (RAW / "acs_block_group_demographics_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
