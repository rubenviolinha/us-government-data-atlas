#!/usr/bin/env python3
"""Extract compact ZIP Code Tabulation Area population estimates from ACS bulk data."""

from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
SOURCE = "https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/acsdt5y2023-b01001.dat"


def number(value):
    return int(value) if value and value.lstrip("-").isdigit() else value


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    with urlopen(Request(SOURCE, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=600) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        indexes = {name: index for index, name in enumerate(header)}
        for line in response:
            if not line.startswith(b"860Z200US"):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            geoid = values[indexes["GEO_ID"]][-5:]
            rows.append({
                "GEO_ID": values[indexes["GEO_ID"]],
                "zcta": geoid,
                "population": number(values[indexes["B01001_E001"]]),
                "population_moe": number(values[indexes["B01001_M001"]]),
                "source": SOURCE,
                "table": "B01001",
            })
    rows.sort(key=lambda row: row["zcta"])
    filename = "zcta_population_acs_2023.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": SOURCE, "records": len(rows), "file": "data/normalized/" + filename, "note": "Compact extraction; raw 200 MB bulk file is intentionally not copied into the repository."}
    (RAW / "zcta_population_acs_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
