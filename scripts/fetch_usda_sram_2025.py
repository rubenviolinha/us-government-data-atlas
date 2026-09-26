#!/usr/bin/env python3
"""Fetch USDA ERS's 2025 SNAP-authorized Retailer Access Map tables."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://ers.usda.gov/media/29395/2025-snap-authorized-retailer-access-map-sram-data.zip?v=12504"
PREFIX = "usda_sram_2025_tracts_part"


def convert(field, raw):
    raw = (raw or "").strip()
    if field == "CensusTract20":
        return raw.zfill(11) if raw else None
    if field in {"State", "County20", "County24"}:
        return raw or None
    if not raw:
        return None
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return raw


def read_table(package, member):
    with package.open(member) as handle:
        text = io.TextIOWrapper(handle, encoding="latin1", newline="")
        return [{key: convert(key, value) for key, value in row.items()} for row in csv.DictReader(text)]


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=180) as response:
        archive = response.read()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        general = read_table(package, "SRAM General Tract Characteristics Data.csv")
        driving = read_table(package, "SRAM Driving Distance Data.csv")
        straight = read_table(package, "SRAM Straight Line Distance Data.csv")
    merged = {row["CensusTract20"]: row for row in general}
    for table in (driving, straight):
        for row in table:
            merged.setdefault(row["CensusTract20"], {}).update(row)
    rows = []
    for tract in sorted(merged):
        row = merged[tract]
        normalized = {key.lower(): value for key, value in row.items()}
        normalized.update({"source": URL, "vintage": "USDA ERS 2025 SNAP-authorized Retailer Access Map", "retrieved_at": retrieved_at})
        rows.append(normalized)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    for old in NORMALIZED.glob(f"{PREFIX}*.json"):
        old.unlink()
    part_size = 7500
    for start in range(0, len(rows), part_size):
        part = start // part_size + 1
        (NORMALIZED / f"{PREFIX}{part}.json").write_text(json.dumps(rows[start:start + part_size], separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://ers.usda.gov/data-products/food-access-research-atlas/download-the-data",
        "format": "Official USDA ERS CSV tables inside ZIP merged by 2020 Census tract and normalized to JSON",
        "license": "U.S. government public data",
        "vintage": "USDA ERS 2025 SNAP-authorized Retailer Access Map",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "parts": (len(rows) + part_size - 1) // part_size,
        "file_prefix": f"data/normalized/{PREFIX}",
        "note": "2020 Census tract food-access characteristics and SNAP-authorized retailer access measures using straight-line and driving distance; no API key used.",
    }
    (RAW / "usda_sram_2025_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
