#!/usr/bin/env python3
"""Fetch Census metropolitan and micropolitan population estimates without an API key."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/metro/totals/cbsa-est2024-alldata.csv"


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    payload = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=120).read()
    (RAW / "census_cbsa_population_2024.csv").write_bytes(payload)
    rows = list(csv.DictReader(io.StringIO(payload.decode("latin-1"))))
    normalized = [{
        "cbsa": row["CBSA"], "name": row["NAME"], "area_type": row["LSAD"],
        "population_2020": row["POPESTIMATE2020"], "population_2021": row["POPESTIMATE2021"],
        "population_2022": row["POPESTIMATE2022"], "population_2023": row["POPESTIMATE2023"],
        "population_2024": row["POPESTIMATE2024"], "source_vintage": "2020-2024"
    } for row in rows if not row["MDIV"] and not row["STCOU"]]
    normalized.sort(key=lambda row: row["cbsa"])
    filename = "cbsa_population_2020_2024.json"
    (NORMALIZED / filename).write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": URL, "records": len(normalized), "file": "data/normalized/" + filename, "note": "Metropolitan and micropolitan statistical areas only; county and metropolitan-division rows excluded."}
    (RAW / "cbsa_population_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
