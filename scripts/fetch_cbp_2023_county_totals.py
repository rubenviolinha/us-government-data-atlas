#!/usr/bin/env python3
"""Fetch keyless 2023 County Business Patterns all-sector totals."""

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
SOURCE_URL = "https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with urlopen(Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=180) as response:
        payload = response.read()
    RAW.mkdir(parents=True, exist_ok=True)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    (RAW / "cbp23co.zip").write_bytes(payload)
    names = {row["GEOID"]: row for row in json.loads((NORMALIZED / "counties_2023.json").read_text(encoding="utf-8"))}
    state_names = {row["abbr"]: row["name"] for row in json.loads((NORMALIZED / "states.json").read_text(encoding="utf-8")) if row.get("abbr")}
    with ZipFile(io.BytesIO(payload)) as archive:
        name = next(name for name in archive.namelist() if name.endswith(".txt"))
        text = archive.read(name).decode("utf-8-sig")
    rows = []
    for raw in csv.DictReader(io.StringIO(text)):
        if raw["naics"] != "------":
            continue
        geoid = raw["fipstate"] + raw["fipscty"]
        county = names.get(geoid, {})
        rows.append({
            "GEOID": geoid, "state_fips": raw["fipstate"], "county_fips": raw["fipscty"],
            "state_name": state_names.get(county.get("USPS")), "county_name": county.get("NAME"), "naics": "00",
            "establishments": int(raw["est"]), "employment": int(raw["emp"]), "first_quarter_payroll_thousands": int(raw["qp1"]), "annual_payroll_thousands": int(raw["ap"]),
            "source": SOURCE_URL, "retrieved_at": retrieved_at, "vintage": "2023 CBP county totals",
        })
    rows.sort(key=lambda row: row["GEOID"])
    output = NORMALIZED / "cbp_county_totals_2023.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": SOURCE_URL, "raw_file": "data/raw/cbp23co.zip", "file": "data/normalized/cbp_county_totals_2023.json", "records": len(rows)}
    (RAW / "cbp_2023_county_totals_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
