#!/usr/bin/env python3
"""Fetch NOAA's public metadata registry for tide and water-level stations."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        payload = json.load(response)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for station in payload.get("stations", []):
        rows.append({
            "station_id": station.get("id"),
            "name": station.get("name"),
            "state": station.get("state"),
            "latitude": station.get("lat"),
            "longitude": station.get("lng"),
            "shef_code": station.get("shefcode"),
            "port_code": station.get("portscode"),
            "affiliations": station.get("affiliations"),
            "timezone": station.get("timezone"),
            "timezone_offset": station.get("timezonecorr"),
            "tidal": station.get("tidal"),
            "great_lakes": station.get("greatlakes"),
            "observed_water_levels": station.get("observedst"),
            "storm_surge": station.get("stormsurge"),
            "forecast": station.get("forecast"),
            "outlook": station.get("outlook"),
            "inundation_database": station.get("inundationdb"),
            "non_navigational": station.get("nonNavigational"),
            "tide_type": station.get("tideType"),
            "station_url": station.get("self"),
            "details_url": (station.get("details") or {}).get("self"),
            "source": URL,
            "vintage": "NOAA tide and water-level station metadata registry",
            "retrieved_at": retrieved_at,
        })
    rows.sort(key=lambda row: row.get("station_id") or "")
    out = ROOT / "data" / "normalized" / "noaa_tide_stations.json"
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://tidesandcurrents.noaa.gov/",
        "vintage": "NOAA tide and water-level station metadata registry",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "count_reported": payload.get("count"),
    }
    manifest_path = ROOT / "data" / "raw" / "noaa_tide_stations_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched {len(rows)} NOAA tide and water-level stations")


if __name__ == "__main__":
    main()
