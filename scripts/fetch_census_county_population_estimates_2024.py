#!/usr/bin/env python3
"""Fetch Census Population Estimates Program 2024 county/state totals."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv"
PREFIX = "census_county_population_estimates_2024"


def value(field, raw):
    raw = (raw or "").strip()
    if field in {"SUMLEV", "REGION", "DIVISION", "STATE", "COUNTY", "STNAME", "CTYNAME"}:
        return raw or None
    if not raw:
        return None
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return raw


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        payload = response.read().decode("latin1")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for raw in csv.DictReader(io.StringIO(payload)):
        row = {field.lower(): value(field, raw.get(field)) for field in raw}
        row.update({"source": URL, "vintage": "Census Population Estimates 2024", "retrieved_at": retrieved_at})
        rows.append(row)
    rows.sort(key=lambda row: (row.get("state") or "", row.get("county") or ""))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    output = NORMALIZED / f"{PREFIX}.json"
    output.write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.census.gov/data/tables/time-series/demo/popest/2020s-counties-total.html",
        "format": "Official Census CSV normalized to JSON",
        "license": "U.S. government public data",
        "vintage": "Census Population Estimates 2024",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "file": f"data/normalized/{output.name}",
        "note": "Annual resident population estimates and estimated components of change for all states and counties, April 1, 2020 through July 1, 2024; no API key used.",
    }
    (RAW / "census_county_population_estimates_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
