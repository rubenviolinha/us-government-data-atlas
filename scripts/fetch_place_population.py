#!/usr/bin/env python3
"""Fetch Census 2020-2024 place population estimates without an API key."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/cities/totals/sub-est2024.csv"


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()
    (RAW / "census_place_population_2024.csv").write_bytes(payload)
    rows = list(csv.DictReader(io.StringIO(payload.decode("latin-1"))))
    rows = [row for row in rows if row["SUMLEV"] == "162"]
    normalized = [
        {
            "GEOID": row["STATE"] + row["PLACE"],
            "state_fips": row["STATE"],
            "place_fips": row["PLACE"],
            "state_name": row["STNAME"],
            "place_name": row["NAME"],
            "population_2020": row["POPESTIMATE2020"],
            "population_2021": row["POPESTIMATE2021"],
            "population_2022": row["POPESTIMATE2022"],
            "population_2023": row["POPESTIMATE2023"],
            "population_2024": row["POPESTIMATE2024"],
            "source_vintage": "2020-2024",
        }
        for row in rows
    ]
    (NORMALIZED / "place_population_2020_2024.json").write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": URL, "records": len(normalized), "file": "data/normalized/place_population_2020_2024.json"}
    (RAW / "place_population_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
