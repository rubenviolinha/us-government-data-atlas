#!/usr/bin/env python3
"""Fetch NOAA/NCEI's public GHCN-Daily station inventory for the United States."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"


def number(value, cast=float):
    value = value.strip()
    try:
        return cast(value) if value else None
    except ValueError:
        return None


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        body = response.read().decode("latin1")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for line in body.splitlines():
        if not line.startswith("US"):
            continue
        rows.append({
            "station_id": line[0:11].strip(),
            "latitude": number(line[12:20]),
            "longitude": number(line[21:30]),
            "elevation_m": number(line[31:37]),
            "state": line[38:40].strip() or None,
            "name": line[41:71].strip(),
            "gsn_flag": line[72:75].strip() or None,
            "hcn_crn_flag": line[75:78].strip() or None,
            "wmo_id": line[79:84].strip() or None,
            "source": URL,
            "vintage": "NOAA/NCEI GHCN-Daily station inventory retrieved 2026-09-26",
            "retrieved_at": retrieved_at,
        })
    rows.sort(key=lambda row: row["station_id"])
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    output = NORMALIZED / "noaa_ghcn_us_stations.json"
    output.write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily",
        "format": "NOAA fixed-width station inventory normalized to JSON",
        "license": "U.S. government public data",
        "vintage": "NOAA/NCEI GHCN-Daily station inventory retrieved 2026-09-26",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "file": "data/normalized/noaa_ghcn_us_stations.json",
        "filter": "station identifiers beginning with US (United States GHCN-Daily stations)",
        "note": "Station metadata only; daily observations are not mirrored in this release.",
    }
    (RAW / "noaa_ghcn_us_stations_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
