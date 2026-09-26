#!/usr/bin/env python3
"""Fetch Census 2024 county age-and-sex population estimates."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/asrh/cc-est2024-agesex-all.csv"
OUTPUT = NORMALIZED / "census_county_age_sex_estimates_2024.json"


def value(field, raw):
    raw = (raw or "").strip()
    if field in {"SUMLEV", "STATE", "COUNTY", "STNAME", "CTYNAME", "YEAR"}:
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
        row.update({"source": URL, "vintage": "Census County Age and Sex Estimates 2024", "retrieved_at": retrieved_at})
        rows.append(row)
    rows.sort(key=lambda row: (row.get("state") or "", row.get("county") or "", row.get("year") or ""))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.census.gov/newsroom/press-kits/2025/2024-population-estimates-characteristics.html",
        "format": "Official Census CSV normalized to JSON",
        "license": "U.S. government public data",
        "vintage": "Census County Age and Sex Estimates 2024",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "file": f"data/normalized/{OUTPUT.name}",
        "note": "Annual county resident population estimates by selected age groups and sex for 2020-2024; no API key used.",
    }
    (RAW / "census_county_age_sex_estimates_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
