#!/usr/bin/env python3
"""Fetch NHTSA's public safety defect investigation table."""

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
URL = "https://static.nhtsa.gov/odi/ffdd/inv/FLAT_INV.zip"
PREFIX = "nhtsa_investigations_part"


def date_value(value):
    value = (value or "").strip()
    if len(value) == 8 and value.isdigit() and value != "00000000":
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return None


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        archive = response.read()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        member = next(name for name in package.namelist() if name.lower().endswith(".txt"))
        with io.TextIOWrapper(package.open(member), encoding="latin1", newline="") as stream:
            for raw in csv.reader(stream, delimiter="\t"):
                if len(raw) != 11:
                    continue
                year = raw[3].strip()
                try:
                    year = int(year) if year and year != "9999" else None
                except ValueError:
                    year = None
                rows.append({
                    "investigation_id": raw[0].strip(),
                    "make": raw[1].strip() or None,
                    "model": raw[2].strip() or None,
                    "model_year": year,
                    "component": raw[4].strip() or None,
                    "manufacturer": raw[5].strip() or None,
                    "opened_date": date_value(raw[6]),
                    "closed_date": date_value(raw[7]),
                    "recall_campaign": raw[8].strip() or None,
                    "subject": raw[9].strip() or None,
                    "summary": raw[10].strip() or None,
                    "source": URL,
                    "vintage": "NHTSA defect investigations retrieved 2026-09-26",
                    "retrieved_at": retrieved_at,
                })
    rows.sort(key=lambda row: (row["investigation_id"], row.get("make") or "", row.get("model") or "", row.get("model_year") or 0))
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
        "source_catalog": "https://www.nhtsa.gov/nhtsa-datasets-and-apis",
        "format": "Official NHTSA tab-delimited text inside ZIP normalized to JSON shards",
        "license": "U.S. government public data",
        "vintage": "NHTSA defect investigations retrieved 2026-09-26",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "parts": (len(rows) + part_size - 1) // part_size,
        "file_prefix": f"data/normalized/{PREFIX}",
        "note": "All NHTSA safety-related defect investigations opened since 1972, including subjects, detailed summaries, dates, and linked recall campaign numbers; no API key used.",
    }
    (RAW / "nhtsa_investigations_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
