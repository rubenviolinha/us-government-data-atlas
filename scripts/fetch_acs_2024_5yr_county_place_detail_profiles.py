#!/usr/bin/env python3
"""Fetch detailed, keyless ACS 2024 5-year county and place profiles."""

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
    "b19001": ("income_distribution", {"B19001_E001", "B19001_M001", *{f"B19001_E{i:03d}" for i in range(2, 18)}}),
    "b01002": ("median_age", {"B01002_E001", "B01002_M001", "B01002_E002", "B01002_E003"}),
    "b25064": ("median_gross_rent", {"B25064_E001", "B25064_M001"}),
    "b25041": ("rooms", {"B25041_E001", "B25041_M001", *{f"B25041_E{i:03d}" for i in range(2, 11)}}),
}
GEO = {
    "county": ("0500000US", "county_geoid", 3222),
    "place": ("1600000US", "place_geoid", 32330),
}


def integer_or_text(value):
    return int(value) if value and value.lstrip("-").isdigit() else value


def fetch(geo_kind, table, fields):
    prefix, geoid_key, expected = GEO[geo_kind]
    source = BASE + f"acsdt5y2024-{table}.dat"
    rows = []
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=900) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        for line in response:
            if not line.startswith(prefix.encode("ascii")):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            raw = dict(zip(header, values))
            geoid = raw["GEO_ID"][len(prefix):]
            row = {key: integer_or_text(value) for key, value in raw.items() if key == "GEO_ID" or key in fields}
            row[geoid_key] = geoid
            rows.append(row)
    if len(rows) != expected:
        raise RuntimeError(f"{geo_kind}/{table}: expected {expected}, got {len(rows)}")
    rows.sort(key=lambda row: row["GEO_ID"])
    return source, rows


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    results = {}
    for geo_kind in GEO:
        for table, (label, fields) in TABLES.items():
            source, rows = fetch(geo_kind, table, fields)
            filename = f"acs_{geo_kind}_{label}_2024_5yr.json"
            output = [{**row, "source": source, "table": table.upper(), "vintage": "2024 ACS 5-year", "retrieved_at": retrieved_at} for row in rows]
            (NORMALIZED / filename).write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
            results[filename] = {"source": source, "table": table.upper(), "records": len(output), "file": "data/normalized/" + filename}
    manifest = {"retrieved_at": retrieved_at, "format": "Joined table-based ACS summary files", "tables": results, "note": "Detailed income-distribution, median-age, median-gross-rent, and rooms profiles for ACS 2024 5-year counties and places; no API key used."}
    (RAW / "acs_county_place_detail_profiles_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
