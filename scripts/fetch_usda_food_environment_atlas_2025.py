#!/usr/bin/env python3
"""Fetch and normalize the USDA ERS 2025 Food Environment Atlas."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www.ers.usda.gov/media/5570/food-environment-atlas-csv-files.zip?v=12636"
OUTPUT = NORMALIZED / "usda_food_environment_atlas_2025_counties.json"
VARIABLE_OUTPUT = NORMALIZED / "usda_food_environment_atlas_2025_variables.json"


def numeric(raw):
    raw = (raw or "").strip()
    if not raw or raw in {"N/A", "NA"}:
        return None
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return raw


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        archive = response.read()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        raw_rows = csv.DictReader(io.TextIOWrapper(package.open("StateAndCountyData.csv"), encoding="utf-8-sig", newline=""))
        by_fips = {}
        for raw in raw_rows:
            fips = raw["FIPS"].strip()
            row = by_fips.setdefault(fips, {"fips": fips, "state": raw["State"].strip(), "county": raw["County"].strip()})
            row[raw["Variable_Code"].strip().lower()] = numeric(raw["Value"])
        variables = []
        for raw in csv.DictReader(io.TextIOWrapper(package.open("VariableList.csv"), encoding="utf-8-sig", newline="")):
            variables.append({key.lower(): (value.strip() if isinstance(value, str) else value) for key, value in raw.items()})
    rows = []
    for fips in sorted(by_fips):
        row = by_fips[fips]
        row.update({"source": URL, "vintage": "USDA ERS Food Environment Atlas 2025", "retrieved_at": retrieved_at})
        rows.append(row)
    for row in variables:
        row.update({"source": URL, "vintage": "USDA ERS Food Environment Atlas 2025", "retrieved_at": retrieved_at})
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    VARIABLE_OUTPUT.write_text(json.dumps(variables, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.ers.usda.gov/data-products/food-environment-atlas/data-access-and-documentation-downloads",
        "format": "Official USDA ERS CSV tables inside ZIP normalized to wide county JSON and variable metadata JSON",
        "license": "U.S. government public data",
        "vintage": "USDA ERS Food Environment Atlas 2025",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "variables": len(variables),
        "file": f"data/normalized/{OUTPUT.name}",
        "variable_file": f"data/normalized/{VARIABLE_OUTPUT.name}",
        "note": "County-level food access, stores, restaurants, local food systems, nutrition assistance, socioeconomic, and community indicators; no API key used.",
    }
    (RAW / "usda_food_environment_atlas_2025_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
