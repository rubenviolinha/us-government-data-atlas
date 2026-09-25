#!/usr/bin/env python3
"""Fetch the keyless Census 2023 ZIP Code Business Patterns totals file."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
SOURCE_URL = "https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23totals.zip"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with urlopen(Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=120) as response:
        payload = response.read()
    RAW.mkdir(parents=True, exist_ok=True)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    (RAW / "zbp23totals.zip").write_bytes(payload)
    with ZipFile(io.BytesIO(payload)) as archive:
        name = next(name for name in archive.namelist() if name.endswith(".txt"))
        text = archive.read(name).decode("utf-8-sig")
    rows = []
    for raw in csv.DictReader(io.StringIO(text)):
        rows.append({
            "zip_code": raw["zip"].zfill(5), "name": raw["name"], "city": raw["city"], "state_abbr": raw["stabbr"], "county_name": raw["cty_name"],
            "establishments": int(raw["est"]), "employment": int(raw["emp"]), "first_quarter_payroll_thousands": int(raw["qp1"]), "annual_payroll_thousands": int(raw["ap"]),
            "employment_suppression": raw["emp_nf"] or None, "first_quarter_payroll_suppression": raw["qp1_nf"] or None, "annual_payroll_suppression": raw["ap_nf"] or None,
            "source": SOURCE_URL, "retrieved_at": retrieved_at, "vintage": "2023 ZBP totals",
        })
    rows.sort(key=lambda row: row["zip_code"])
    output = NORMALIZED / "zbp_totals_2023.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": SOURCE_URL, "raw_file": "data/raw/zbp23totals.zip", "file": "data/normalized/zbp_totals_2023.json", "records": len(rows)}
    (RAW / "zbp_2023_totals_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
