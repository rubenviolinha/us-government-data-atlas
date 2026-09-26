#!/usr/bin/env python3
"""Fetch keyless NOAA Climate at a Glance annual state climate series."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
# NOAA's statewide series codes are an agency-specific ordering, not FIPS.
STATES = {
    1: "AL", 2: "AZ", 3: "AR", 4: "CA", 5: "CO", 6: "CT", 7: "DE", 8: "FL", 9: "GA", 10: "ID",
    11: "IL", 12: "IN", 13: "IA", 14: "KS", 15: "KY", 16: "LA", 17: "ME", 18: "MD", 19: "MA", 20: "MI",
    21: "MN", 22: "MS", 23: "MO", 24: "MT", 25: "NE", 26: "NV", 27: "NH", 28: "NJ", 29: "NM", 30: "NY",
    31: "NC", 32: "ND", 33: "OH", 34: "OK", 35: "OR", 36: "PA", 37: "RI", 38: "SC", 39: "SD", 40: "TN",
    41: "TX", 42: "UT", 43: "VT", 44: "VA", 45: "WA", 46: "WV", 47: "WI", 48: "WY", 50: "AK", 51: "HI",
}


def fetch(code, parameter):
    url = f"https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/statewide/time-series/{code}/{parameter}/12/12/1895-2025.json"
    payload = json.load(urlopen(Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=120))
    return url, payload


def main():
    rows = []
    sources = set()
    for code, abbr in STATES.items():
        for parameter, field in (("tavg", "annual_avg_temperature_f"), ("pcp", "annual_precipitation_inches")):
            url, payload = fetch(code, parameter)
            sources.add(url)
            for period, value in payload["data"].items():
                year = int(period[:4])
                rows.append({"state_climate_code": str(code), "state_abbr": abbr, "year": year, "parameter": field, "value": value.get("value"), "units": payload["description"].get("units"), "source": url})
    rows.sort(key=lambda row: (row["state_abbr"], row["year"], row["parameter"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    filename = "noaa_state_climate_1895_2025.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "sources": sorted(sources), "format": "NOAA Climate at a Glance JSON", "records": len(rows), "states": len(STATES), "file": "data/normalized/" + filename, "note": "Annual January-December statewide average temperature and precipitation series; no API key used. NOAA agency state codes are preserved separately from FIPS codes."}
    (RAW / "noaa_state_climate_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
