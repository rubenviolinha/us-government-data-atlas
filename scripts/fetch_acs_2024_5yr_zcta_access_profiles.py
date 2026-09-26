#!/usr/bin/env python3
"""Fetch keyless ACS 2024 5-year ZCTA access and housing-burden profiles."""

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
    "b08301": ("commuting", {"B08301_E001", "B08301_M001", "B08301_E002", "B08301_E003", "B08301_E004", "B08301_E005"}),
    "b25044": ("vehicles", {"B25044_E001", "B25044_M001", "B25044_E002", "B25044_E003", "B25044_E004", "B25044_E005"}),
    "b28002": ("internet", {"B28002_E001", "B28002_M001", "B28002_E002", "B28002_E003", "B28002_E004", "B28002_E005"}),
    "b25070": ("rent_burden", {"B25070_E001", "B25070_M001", "B25070_E002", "B25070_E003", "B25070_E004", "B25070_E005"}),
}
PREFIX = "860Z200US"
EXPECTED = 33772


def integer_or_text(value):
    return int(value) if value and value.lstrip("-").isdigit() else value


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
            row = {k: integer_or_text(v) for k, v in raw.items() if k == "GEO_ID" or k in fields}
            row["zcta"] = geoid
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
        filename = f"acs_zcta_{label}_2024_5yr.json"
        output = [{**row, "source": source, "table": table.upper(), "vintage": "2024 ACS 5-year", "retrieved_at": retrieved_at} for row in rows]
        (NORMALIZED / filename).write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
        results[filename] = {"source": source, "table": table.upper(), "records": len(output), "file": "data/normalized/" + filename}
    manifest = {"retrieved_at": retrieved_at, "format": "Joined table-based ACS summary files", "tables": results, "note": "Keyless ACS 2024 5-year commuting, vehicle availability, internet access, and rent-burden profiles for all 33,772 ACS-covered ZCTAs."}
    (RAW / "acs_zcta_access_profiles_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
