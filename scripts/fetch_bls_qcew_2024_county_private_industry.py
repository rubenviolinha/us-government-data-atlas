#!/usr/bin/env python3
"""Fetch 2024 BLS QCEW state and county private-sector industry summaries."""

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
URL = "https://data.bls.gov/cew/data/files/2024/csv/2024_annual_by_area.zip"


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
    with urlopen(request, timeout=240) as response:
        archive = response.read()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        for member in package.namelist():
            basename = member.rsplit("/", 1)[-1]
            area_token = basename.split("annual ", 1)[-1][:5]
            if member.endswith("/") or not area_token.isdigit():
                continue
            with io.TextIOWrapper(package.open(member), encoding="latin1") as stream:
                for raw in csv.DictReader(stream):
                    # Private-sector state/county rows at sector/subsector level; the
                    # aggregate all-industry rows are kept in the companion file.
                    if raw.get("own_code") != "5" or raw.get("qtr") != "A" or len(raw.get("industry_code", "")) not in {2, 3}:
                        continue
                    rows.append({
                        "area_fips": raw["area_fips"],
                        "area_title": raw.get("area_title"),
                        "industry_code": raw["industry_code"],
                        "industry_title": raw.get("industry_title"),
                        "ownership_code": raw["own_code"],
                        "ownership_title": raw.get("own_title"),
                        "aggregation_level_code": raw["agglvl_code"],
                        "aggregation_level_title": raw.get("agglvl_title"),
                        "year": number(raw["year"]),
                        "average_establishments": number(raw.get("annual_avg_estabs_count")),
                        "average_employment": number(raw.get("annual_avg_emplvl")),
                        "total_annual_wages": number(raw.get("total_annual_wages")),
                        "average_weekly_wage": number(raw.get("annual_avg_wkly_wage")),
                        "average_annual_pay": number(raw.get("avg_annual_pay")),
                        "employment_percent_change": number(raw.get("oty_annual_avg_emplvl_pct_chg"), float),
                        "wages_percent_change": number(raw.get("oty_total_annual_wages_pct_chg"), float),
                        "source": URL,
                        "vintage": "BLS QCEW 2024 county private industry release",
                        "retrieved_at": retrieved_at,
                    })
    rows.sort(key=lambda row: (row["area_fips"], row["industry_code"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    part_size = 30000
    for index in range(0, len(rows), part_size):
        part = index // part_size + 1
        out = NORMALIZED / f"bls_qcew_2024_county_private_industry_part{part}.json"
        out.write_text(json.dumps(rows[index:index + part_size], indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.bls.gov/cew/",
        "format": "ZIP CSV normalized to JSON shards",
        "license": "U.S. government public data",
        "vintage": "BLS QCEW 2024 county private industry release",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "parts": (len(rows) + part_size - 1) // part_size,
        "filter": "state and county files, own_code=5, qtr=A, industry_code length 2 or 3",
        "file_prefix": "data/normalized/bls_qcew_2024_county_private_industry_part",
        "note": "Private-sector state/county industry summaries with establishment, employment, wage, and change metrics; no API key used.",
    }
    (RAW / "bls_qcew_2024_county_private_industry_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
