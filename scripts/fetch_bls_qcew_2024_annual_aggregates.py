#!/usr/bin/env python3
"""Fetch aggregate 2024 BLS Quarterly Census of Employment and Wages data."""

from datetime import datetime, timezone
import csv
import io
import json
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://data.bls.gov/cew/data/files/2024/csv/2024_annual_singlefile.zip"


def number(value, cast=int):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return cast(value)
    except ValueError:
        return None


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=180) as response:
        archive = response.read()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        with io.TextIOWrapper(package.open(package.namelist()[0]), encoding="latin1") as stream:
            for raw in csv.DictReader(stream):
                # Keep annual all-industry/all-ownership aggregates across all
                # geographic levels published by the official single-file release.
                if raw.get("industry_code") != "10" or raw.get("own_code") != "0" or raw.get("qtr") != "A":
                    continue
                row = {
                    "area_fips": raw["area_fips"],
                    "ownership_code": raw["own_code"],
                    "industry_code": raw["industry_code"],
                    "aggregation_level_code": raw["agglvl_code"],
                    "size_code": raw["size_code"],
                    "year": number(raw["year"]),
                    "quarter": raw["qtr"],
                    "disclosure_code": raw.get("disclosure_code") or None,
                    "average_establishments": number(raw.get("annual_avg_estabs")),
                    "average_employment": number(raw.get("annual_avg_emplvl")),
                    "total_annual_wages": number(raw.get("total_annual_wages")),
                    "taxable_annual_wages": number(raw.get("taxable_annual_wages")),
                    "annual_contributions": number(raw.get("annual_contributions")),
                    "average_weekly_wage": number(raw.get("annual_avg_wkly_wage")),
                    "average_annual_pay": number(raw.get("avg_annual_pay")),
                    "employment_change": number(raw.get("oty_annual_avg_emplvl_chg")),
                    "employment_percent_change": number(raw.get("oty_annual_avg_emplvl_pct_chg"), float),
                    "wages_change": number(raw.get("oty_total_annual_wages_chg")),
                    "wages_percent_change": number(raw.get("oty_total_annual_wages_pct_chg"), float),
                    "source": URL,
                    "vintage": "BLS QCEW 2024 annual aggregate release",
                    "retrieved_at": retrieved_at,
                }
                rows.append(row)
    rows.sort(key=lambda row: (row["aggregation_level_code"], row["area_fips"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    filename = "bls_qcew_2024_annual_aggregates.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.bls.gov/cew/",
        "format": "ZIP CSV normalized to JSON",
        "license": "U.S. government public data",
        "vintage": "BLS QCEW 2024 annual aggregate release",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "aggregate_filter": "industry_code=10, own_code=0, qtr=A",
        "file": "data/normalized/" + filename,
        "note": "All-industry/all-ownership annual aggregate rows across the published QCEW geographic aggregation levels; no API key used.",
    }
    (RAW / "bls_qcew_2024_annual_aggregates_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
