#!/usr/bin/env python3
"""Fetch NOAA/NCEI IBTrACS North Atlantic and North Pacific track points."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NA.list.v04r01.csv"
PREFIX = "noaa_ibtracs_north_atlantic_part"

CORE = ["SID", "SEASON", "NUMBER", "BASIN", "SUBBASIN", "NAME", "ISO_TIME", "NATURE", "LAT", "LON", "WMO_WIND", "WMO_PRES", "DIST2LAND", "LANDFALL", "USA_ATCF_ID", "USA_STATUS", "USA_WIND", "USA_PRES", "USA_SSHS", "USA_LAT", "USA_LON", "USA_RECORD", "STORM_SPEED", "STORM_DIR"]


def value(field, raw):
    raw = (raw or "").strip()
    if not raw or raw in {"NA", "-999", "-999.0"}:
        return None
    if field in {"SID", "BASIN", "SUBBASIN", "NAME", "ISO_TIME", "NATURE", "USA_ATCF_ID", "USA_STATUS", "USA_RECORD"}:
        return raw
    try:
        return float(raw) if any(ch in raw for ch in ".Ee") else int(raw)
    except ValueError:
        return raw


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=180) as response:
        payload = response.read().decode("latin1")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    reader = csv.DictReader(io.StringIO(payload))
    for raw in reader:
        if not raw.get("SID", "").strip() or raw.get("SEASON", "").strip() == "Year":
            continue
        row = {field.lower(): value(field, raw.get(field)) for field in CORE}
        row.update({"source": URL, "vintage": "NOAA/NCEI IBTrACS North Atlantic v04r01", "retrieved_at": retrieved_at})
        rows.append(row)
    rows.sort(key=lambda row: (row.get("sid") or "", row.get("iso_time") or ""))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    for old in NORMALIZED.glob(f"{PREFIX}*.json"):
        old.unlink()
    part_size = 10000
    for start in range(0, len(rows), part_size):
        part = start // part_size + 1
        (NORMALIZED / f"{PREFIX}{part}.json").write_text(json.dumps(rows[start:start + part_size], separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.ncei.noaa.gov/products/international-best-track-archive",
        "format": "Official NOAA/NCEI CSV normalized to JSON shards",
        "license": "U.S. government public data",
        "vintage": "NOAA/NCEI IBTrACS North Atlantic v04r01",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "parts": (len(rows) + part_size - 1) // part_size,
        "file_prefix": f"data/normalized/{PREFIX}",
        "note": "Historical tropical-cyclone track points with position, wind, pressure, status, distance-to-land, and storm-motion fields; no API key used.",
    }
    (RAW / "noaa_ibtracs_north_atlantic_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
