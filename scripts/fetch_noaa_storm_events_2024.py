#!/usr/bin/env python3
"""Fetch NOAA/NCEI's official 2024 Storm Events detail release."""

from datetime import datetime, timezone
import csv
import gzip
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2024_c20260728.csv.gz"


def number(value, cast=int):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return cast(value)
    except ValueError:
        return None


def damage(value):
    """Convert NOAA's compact damage code (e.g. 2.5K, 1.00M) to dollars."""
    value = (value or "").strip().upper()
    if not value:
        return None
    multiplier = 1
    if value[-1:] in {"K", "M", "B", "T"}:
        multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000, "T": 1_000_000_000_000}[value[-1]]
        value = value[:-1]
    try:
        return round(float(value) * multiplier, 2)
    except ValueError:
        return None


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=180) as response:
        text = gzip.decompress(response.read()).decode("latin1")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    fields = (
        "BEGIN_DATE_TIME", "END_DATE_TIME", "EPISODE_ID", "EVENT_ID", "STATE", "STATE_FIPS",
        "YEAR", "MONTH_NAME", "EVENT_TYPE", "CZ_TYPE", "CZ_FIPS", "CZ_NAME", "WFO",
        "CZ_TIMEZONE", "INJURIES_DIRECT", "INJURIES_INDIRECT", "DEATHS_DIRECT", "DEATHS_INDIRECT",
        "DAMAGE_PROPERTY", "DAMAGE_CROPS", "SOURCE", "MAGNITUDE", "MAGNITUDE_TYPE", "FLOOD_CAUSE",
        "CATEGORY", "TOR_F_SCALE", "TOR_LENGTH", "TOR_WIDTH", "BEGIN_LOCATION", "END_LOCATION",
        "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON", "DATA_SOURCE",
    )
    for raw in csv.DictReader(io.StringIO(text)):
        if not raw.get("EVENT_ID"):
            continue
        row = {key.lower(): (raw.get(key) or "").strip() or None for key in fields}
        for key in ("year", "state_fips", "cz_fips", "injuries_direct", "injuries_indirect", "deaths_direct", "deaths_indirect"):
            row[key] = number(row[key])
        for key in ("magnitude", "tor_length", "tor_width", "begin_lat", "begin_lon", "end_lat", "end_lon"):
            row[key] = number(row[key], float)
        row["property_damage_usd"] = damage(row["damage_property"])
        row["crop_damage_usd"] = damage(row["damage_crops"])
        row["source"] = URL
        row["vintage"] = "NOAA/NCEI Storm Events details 2024"
        row["retrieved_at"] = retrieved_at
        rows.append(row)
    rows.sort(key=lambda row: (row["state"] or "", row["begin_date_time"] or "", row["event_id"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    part_size = 30000
    for index in range(0, len(rows), part_size):
        part = index // part_size + 1
        out = NORMALIZED / f"noaa_storm_events_2024_part{part}.json"
        out.write_text(json.dumps(rows[index:index + part_size], indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.ncei.noaa.gov/stormevents/",
        "format": "GZIP CSV normalized to JSON",
        "license": "U.S. government public data",
        "vintage": "NOAA/NCEI Storm Events details 2024",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "raw_bytes": len(text.encode("latin1")),
        "parts": (len(rows) + part_size - 1) // part_size,
        "file_prefix": "data/normalized/noaa_storm_events_2024_part",
        "note": "Official event-level storm reports with geography, timing, casualties, damage codes/estimates, and coordinates; no API key used.",
    }
    (RAW / "noaa_storm_events_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
