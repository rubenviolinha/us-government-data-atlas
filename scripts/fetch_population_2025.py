#!/usr/bin/env python3
"""Fetch Census 2020-2025 population estimates from public bulk CSV files."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/"
YEARS = range(2020, 2026)

def read_csv(path):
    url = BASE + path
    payload = urlopen(Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300).read()
    raw_name = Path(path).name
    (RAW / ("census_2025_" + raw_name)).write_bytes(payload)
    return url, list(csv.DictReader(io.StringIO(payload.decode("latin-1"))))

def estimates(row):
    return {f"population_{year}": row[f"POPESTIMATE{year}"] for year in YEARS}

def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    outputs = {}
    url, rows = read_csv("state/totals/NST-EST2025-ALLDATA.csv")
    data = [{"state_fips": r["STATE"], "state_name": r["NAME"], **estimates(r), "source_vintage": "2020-2025"} for r in rows if r["SUMLEV"] == "040"]
    outputs["state_population_2020_2025.json"] = (url, data)
    url, rows = read_csv("counties/totals/co-est2025-alldata.csv")
    data = [{"GEOID": r["STATE"] + r["COUNTY"], "state_fips": r["STATE"], "county_fips": r["COUNTY"], "state_name": r["STNAME"], "county_name": r["CTYNAME"], **estimates(r), "source_vintage": "2020-2025"} for r in rows if r["SUMLEV"] == "050"]
    outputs["county_population_2020_2025.json"] = (url, data)
    url, rows = read_csv("cities/totals/sub-est2025.csv")
    data = [{"GEOID": r["STATE"] + r["PLACE"], "state_fips": r["STATE"], "place_fips": r["PLACE"], "state_name": r["STNAME"], "place_name": r["NAME"], **estimates(r), "source_vintage": "2020-2025"} for r in rows if r["SUMLEV"] == "162"]
    outputs["place_population_2020_2025.json"] = (url, data)
    url, rows = read_csv("metro/totals/cbsa-est2025-alldata.csv")
    data = [{"cbsa": r["CBSA"], "name": r["NAME"], "area_type": r["LSAD"], **estimates(r), "source_vintage": "2020-2025"} for r in rows if not r["MDIV"] and not r["STCOU"]]
    outputs["cbsa_population_2020_2025.json"] = (url, data)
    url, rows = read_csv("metro/totals/csa-est2025-alldata.csv")
    data = [{"csa": r["CSA"], "name": r["NAME"], "area_type": r["LSAD"], **estimates(r), "source_vintage": "2020-2025"} for r in rows if r["LSAD"] == "Combined Statistical Area"]
    outputs["csa_population_2020_2025.json"] = (url, data)
    manifest = {"retrieved_at": retrieved_at, "vintage": "2020-2025", "files": []}
    for filename, (url, data) in outputs.items():
        data.sort(key=lambda row: row.get("GEOID") or row.get("state_fips") or row.get("cbsa") or row.get("csa"))
        (NORMALIZED / filename).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        manifest["files"].append({"file": "data/normalized/" + filename, "source": url, "records": len(data)})
    (RAW / "population_2025_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
