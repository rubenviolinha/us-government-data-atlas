#!/usr/bin/env python3
"""Extract compact 2024 ACS 5-year ZCTA population and profile fields."""

from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/"
TABLES = {"median_household_income": ("b19013", "B19013_E001"), "housing_units": ("b25001", "B25001_E001"), "race_total": ("b02001", "B02001_E001"), "poverty_universe": ("b17001", "B17001_E001"), "education_universe": ("b15003", "B15003_E001")}


def number(value):
    return int(value) if value and value.lstrip("-").isdigit() else value


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    profiles, populations, sources = {}, [], {}
    for output_field, (table, field) in TABLES.items():
        source = BASE + f"acsdt5y2024-{table}.dat"
        sources[output_field] = source
        with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=600) as response:
            header = response.readline().decode("utf-8").rstrip("\n").split("|")
            indexes = {name: index for index, name in enumerate(header)}
            for line in response:
                if not line.startswith(b"860Z200US"):
                    continue
                cells = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
                geoid = cells[indexes["GEO_ID"]][-5:]
                parsed = number(cells[indexes[field]])
                profiles.setdefault(geoid, {"zcta": geoid, "source_vintage": "ACS 2024 5-year"})[output_field] = parsed
                if output_field == "race_total":
                    populations.append({"GEO_ID": cells[indexes["GEO_ID"]], "zcta": geoid, "population": parsed, "population_moe": number(cells[indexes["B02001_M001"]]), "source": source, "table": "B02001"})
    rows = sorted(profiles.values(), key=lambda row: row["zcta"])
    (DATA / "zcta_profiles_acs_2024.json").write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    populations.sort(key=lambda row: row["zcta"])
    population_source = BASE + "acsdt5y2024-b01001.dat"
    with urlopen(Request(population_source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=600) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        indexes = {name: index for index, name in enumerate(header)}
        populations = []
        for line in response:
            if line.startswith(b"860Z200US"):
                cells = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
                populations.append({"GEO_ID": cells[indexes["GEO_ID"]], "zcta": cells[indexes["GEO_ID"]][-5:], "population": number(cells[indexes["B01001_E001"]]), "population_moe": number(cells[indexes["B01001_M001"]]), "source": population_source, "table": "B01001"})
    populations.sort(key=lambda row: row["zcta"])
    (DATA / "zcta_population_acs_2024.json").write_text(json.dumps(populations, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "sources": {**sources, "population": population_source}, "records": len(rows), "file": "data/normalized/zcta_profiles_acs_2024.json", "note": "Compact 2024 ACS 5-year ZCTA population and headline profile extraction; no API key used."}
    (RAW / "zcta_acs_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
