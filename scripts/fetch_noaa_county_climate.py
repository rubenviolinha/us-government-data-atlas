#!/usr/bin/env python3
"""Fetch keyless NOAA Climate at a Glance annual county series."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/time-series"
PARAMETERS = (("tavg", "annual_avg_temperature"), ("pcp", "annual_precipitation"))
PARTS = 4


def fetch_county(county, parameter, label):
    geoid = county["GEOID"]
    location = f"{county['USPS']}-{geoid[2:]}"
    url = f"{BASE}/{location}/{parameter}/12/12/1895-2024.json"
    try:
        payload = json.load(urlopen(Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=60))
    except (HTTPError, URLError, TimeoutError) as exc:
        return [], {"geoid": geoid, "location": location, "error": str(exc)}
    units = payload.get("description", {}).get("units")
    rows = []
    for period, item in payload.get("data", {}).items():
        rows.append({
            "county_geoid": geoid,
            "county_name": county["NAME"],
            "state_abbr": county["USPS"],
            "year": int(period[:4]),
            "parameter": label,
            "value": item.get("value"),
            "units": units,
            "source": url,
        })
    return rows, None


def main():
    counties = json.loads((NORMALIZED / "counties_2024.json").read_text(encoding="utf-8"))
    retrieved_at = datetime.now(timezone.utc).isoformat()
    results = {label: [] for _parameter, label in PARAMETERS}
    missing = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(fetch_county, county, parameter, label) for county in counties for parameter, label in PARAMETERS]
        for future in as_completed(futures):
            rows, error = future.result()
            if error:
                missing.append(error)
            elif rows:
                results[rows[0]["parameter"]].extend(rows)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    files = {}
    for label, rows in results.items():
        rows.sort(key=lambda row: (row["county_geoid"], row["year"]))
        part_files = []
        for index in range(PARTS):
            start = (len(rows) * index) // PARTS
            end = (len(rows) * (index + 1)) // PARTS
            filename = f"noaa_county_climate_{label}_1895_2024_part{index + 1}.json"
            part = rows[start:end]
            (NORMALIZED / filename).write_text(json.dumps(part, separators=(",", ":")) + "\n", encoding="utf-8")
            part_files.append({"file": "data/normalized/" + filename, "records": len(part), "counties": len({row["county_geoid"] for row in part})})
        files[label] = {"records": len(rows), "counties": len({row["county_geoid"] for row in rows}), "parts": part_files}
    manifest = {"retrieved_at": retrieved_at, "sources": [BASE], "format": "NOAA Climate at a Glance JSON", "files": files, "requested_counties": len(counties), "missing_series": missing, "note": "Annual January-December county average temperature and precipitation series; no API key used. NOAA does not publish a series for every Census county-equivalent, so unavailable locations are preserved in missing_series."}
    (RAW / "noaa_county_climate_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
