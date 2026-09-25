#!/usr/bin/env python3
"""Fetch compact 2024 ACS 5-year profiles for additional Census geographies."""

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
GEOGRAPHIES = {
    "consolidated_city": ("1700000US", 8),
    "alaska_native_regional_corporation": ("2300000US", 12),
    "principal_city": ("312M700US", 1294),
    "metropolitan_division": ("314M700US", 37),
    "subminor_civil_division": ("0670000US", 145),
    "tribal_subdivision_or_remainder": ("2510000US", 493),
    "american_indian_area_reservation_statistical": ("2520000US", 617),
    "off_reservation_trust_land_hawaiian_homeland": ("2540000US", 247),
    "tribal_census_tract": ("2560000US", 493),
    "tribal_block_group": ("2580000US", 935),
}


def integer_or_text(value):
    return int(value) if value.lstrip("-").isdigit() else value


def fetch(table, table_label, fields, retrieved_at):
    source = BASE + f"acsdt5y2024-{table}.dat"
    rows_by_type = {geo_type: [] for geo_type in GEOGRAPHIES}
    prefixes = {prefix: geo_type for geo_type, (prefix, _expected) in GEOGRAPHIES.items()}
    with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=600) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        for line in response:
            match = next(((prefix, kind) for prefix, kind in prefixes.items() if line.startswith(prefix.encode("ascii"))), None)
            if match is None:
                continue
            prefix, geo_type = match
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            raw = dict(zip(header, values))
            geoid = raw["GEO_ID"][len(prefix):]
            row = {key: integer_or_text(value) for key, value in raw.items() if key == "GEO_ID" or key in fields}
            row.update({"geography_geoid": geoid, "geography_type": geo_type, "source": source, "table": table_label, "vintage": "2024 ACS 5-year", "retrieved_at": retrieved_at})
            rows_by_type[geo_type].append(row)
    return source, rows_by_type


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    results = {}
    for table, (label, table_name, fields) in TABLES.items():
        source, rows_by_type = fetch(table, table_name, fields, retrieved_at)
        suffix = label.lower().replace('b01001', 'age_sex').replace('b15003', 'education').replace('b17001', 'poverty').replace('b19013', 'income').replace('b25001', 'housing').replace('b02001', 'race')
        for geo_type, (_prefix, expected) in GEOGRAPHIES.items():
            rows = sorted(rows_by_type[geo_type], key=lambda row: row["GEO_ID"])
            if geo_type == "tribal_block_group" and table == "b17001":
                expected = 0
            if len(rows) != expected:
                raise RuntimeError(f"{geo_type} {label}: expected {expected}, got {len(rows)}")
            filename = f"acs_{geo_type}_{suffix}_2024_5yr.json"
            (NORMALIZED / filename).write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
            results[filename] = {"source": source, "file": "data/normalized/" + filename, "records": len(rows)}
    manifest = {"retrieved_at": retrieved_at, "tables": results, "note": "Public table-based ACS 2024 5-year compact profiles for consolidated cities and Alaska Native Regional Corporations; no API key used."}
    (RAW / "acs_special_geographies_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
