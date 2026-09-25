#!/usr/bin/env python3
"""Fetch keyless 2023 County Business Patterns all-sector CBSA totals."""

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
SOURCE_URL = "https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23msa.zip"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with urlopen(Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=180) as response:
        payload = response.read()
    RAW.mkdir(parents=True, exist_ok=True)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    (RAW / "cbp23msa.zip").write_bytes(payload)
    names = {row["cbsa"]: row for row in json.loads((NORMALIZED / "cbsa_population_2020_2024.json").read_text(encoding="utf-8"))}
    with ZipFile(io.BytesIO(payload)) as archive:
        name = next(name for name in archive.namelist() if name.endswith(".txt"))
        text = archive.read(name).decode("utf-8-sig")
    rows = []
    for raw in csv.DictReader(io.StringIO(text)):
        if raw["naics"] != "------":
            continue
        cbsa = raw["msa"]
        rows.append({
            "cbsa": cbsa, "name": names.get(cbsa, {}).get("name"), "naics": "00",
            "establishments": int(raw["est"]), "employment": int(raw["emp"]), "first_quarter_payroll_thousands": int(raw["qp1"]), "annual_payroll_thousands": int(raw["ap"]),
            "source": SOURCE_URL, "retrieved_at": retrieved_at, "vintage": "2023 CBP CBSA totals",
        })
    rows.sort(key=lambda row: row["cbsa"])
    output = NORMALIZED / "cbp_cbsa_totals_2023.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": SOURCE_URL, "raw_file": "data/raw/cbp23msa.zip", "file": "data/normalized/cbp_cbsa_totals_2023.json", "records": len(rows)}
    (RAW / "cbp_2023_cbsa_totals_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
