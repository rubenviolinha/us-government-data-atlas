#!/usr/bin/env python3
"""Fetch EPA Facility Registry Service national facility records.

The EPA national single-file archive is large, so this script streams the CSV
from the ZIP and writes compact JSON shards containing the stable identity,
address, geography, and coordinate fields most users need.
"""

from datetime import datetime, timezone
import csv
import io
import json
import os
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://ordsext.epa.gov/FLA/www3/state_files/national_single.zip"
PREFIX = "epa_frs_facilities_2026_part"


def first(row, *names):
    for name in names:
        value = row.get(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    for old in NORMALIZED.glob(f"{PREFIX}*.json"):
        old.unlink()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    total = 0
    part_size = 25000
    part = 0

    local_archive = os.environ.get("EPA_FRS_ARCHIVE")
    if local_archive:
        archive_source = open(local_archive, "rb")
    else:
        archive_source = urlopen(request, timeout=900)
    with archive_source:
        with zipfile.ZipFile(io.BytesIO(archive_source.read())) as archive:
            member = next(name for name in archive.namelist() if name.upper().endswith("NATIONAL_SINGLE.CSV"))
            with archive.open(member) as raw_stream:
                stream = (line.decode("latin1") for line in raw_stream)
                for raw in csv.DictReader(stream):
                    record = {
                        "registry_id": first(raw, "REGISTRY_ID", "REGISTRYID", "FACILITY_ID"),
                        "facility_name": first(raw, "FAC_NAME", "FACILITY_NAME", "FACILITYNAME", "PRIMARY_NAME"),
                        "street": first(raw, "LOCATION_ADDRESS", "STREET_ADDRESS", "ADDRESS"),
                        "city": first(raw, "CITY_NAME", "CITY"),
                        "state": first(raw, "STATE_CODE", "STATE"),
                        "zip": first(raw, "ZIP_CODE", "ZIP", "POSTAL_CODE"),
                        "county": first(raw, "COUNTY_NAME", "COUNTY"),
                        "epa_region": first(raw, "EPA_REGION", "EPA_REGION_CODE", "REGION"),
                        "latitude": first(raw, "LATITUDE83", "LATITUDE", "LAT"),
                        "longitude": first(raw, "LONGITUDE83", "LONGITUDE", "LON", "LONG"),
                        "source": URL,
                        "vintage": "EPA FRS national facilities as of 2026-09-01",
                        "retrieved_at": retrieved_at,
                    }
                    if not record["registry_id"] or not record["facility_name"]:
                        continue
                    for key in ("latitude", "longitude"):
                        if record[key]:
                            try:
                                record[key] = float(record[key])
                            except ValueError:
                                record[key] = None
                    rows.append(record)
                    total += 1
                    if len(rows) >= part_size:
                        part += 1
                        (NORMALIZED / f"{PREFIX}{part}.json").write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
                        rows = []
    if rows:
        part += 1
        (NORMALIZED / f"{PREFIX}{part}.json").write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")

    manifest = {
        "source": URL,
        "source_catalog": "https://www.epa.gov/frs/epa-frs-facilities-state-single-file-csv-download",
        "format": "EPA national CSV inside ZIP normalized to JSON shards",
        "license": "U.S. government public data",
        "vintage": "EPA FRS national facilities as of 2026-09-01",
        "retrieved_at": retrieved_at,
        "records": total,
        "parts": part,
        "file_prefix": f"data/normalized/{PREFIX}",
        "fields": "registry_id, facility_name, street, city, state, zip, county, epa_region, latitude, longitude",
        "note": "Core facility identity, address, geography, and coordinates; source archive includes additional EPA program columns.",
    }
    (RAW / "epa_frs_facilities_2026_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
