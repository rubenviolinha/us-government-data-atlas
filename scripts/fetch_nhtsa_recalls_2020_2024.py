#!/usr/bin/env python3
"""Fetch NHTSA's public 2020-2024 recall campaign table."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
import zipfile
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://static.nhtsa.gov/odi/ffdd/rcl/RCL_FROM_2020_2024.zip"
PREFIX = "nhtsa_recalls_2020_2024_part"


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        archive = response.read()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        member = next(name for name in package.namelist() if name.lower().endswith(".csv"))
        with io.TextIOWrapper(package.open(member), encoding="latin1") as stream:
            for raw in csv.DictReader(stream):
                year = (raw.get("MODEL YEAR") or "").strip()
                try:
                    year = int(year)
                except ValueError:
                    year = None
                rows.append({
                    "nhtsa_id": (raw.get("NHTSA ID") or "").strip(),
                    "document_name": (raw.get("DOCUMENT NAME") or "").strip() or None,
                    "make": (raw.get("MAKE") or "").strip() or None,
                    "model": (raw.get("MODEL") or "").strip() or None,
                    "model_year": year,
                    "summary": (raw.get("SUMMARY") or "").strip() or None,
                    "source": URL,
                    "vintage": "NHTSA recall campaigns 2020-2024",
                    "retrieved_at": retrieved_at,
                })
    rows.sort(key=lambda row: (row["nhtsa_id"], row.get("make") or "", row.get("model") or "", row.get("model_year") or 0))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    for old in NORMALIZED.glob(f"{PREFIX}*.json"):
        old.unlink()
    part_size = 15000
    for start in range(0, len(rows), part_size):
        part = start // part_size + 1
        (NORMALIZED / f"{PREFIX}{part}.json").write_text(json.dumps(rows[start:start + part_size], separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.nhtsa.gov/nhtsa-datasets-and-apis",
        "format": "Official NHTSA CSV inside ZIP normalized to JSON shards",
        "license": "U.S. government public data",
        "vintage": "NHTSA recall campaigns 2020-2024",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "parts": (len(rows) + part_size - 1) // part_size,
        "file_prefix": f"data/normalized/{PREFIX}",
        "note": "Recall campaign document metadata and safety summaries for vehicles and equipment; no API key used.",
    }
    (RAW / "nhtsa_recalls_2020_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
