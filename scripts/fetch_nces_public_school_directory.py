#!/usr/bin/env python3
"""Fetch the public NCES Common Core of Data school directory.

The CCD publishes the current public-school universe as a downloadable CSV
inside a ZIP archive.  This release keeps the stable identifiers, names,
addresses, contact fields, status, charter flag, school type, and grade range
in two repository-safe JSON parts.
"""

from datetime import datetime, timezone
import csv
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
URL = "https://nces.ed.gov/ccd/Data/zip/ccd_sch_029_2425_w_0a_051425.zip"

FIELDS = [
    "SCHOOL_YEAR", "NCESSCH", "LEAID", "ST_SCHID", "SCH_NAME", "LEA_NAME",
    "STATENAME", "ST", "MCITY", "MSTATE", "MZIP", "LSTREET1", "LCITY",
    "LSTATE", "LZIP", "PHONE", "WEBSITE", "SY_STATUS_TEXT",
    "SCH_TYPE_TEXT", "CHARTER_TEXT", "GSLO", "GSHI", "LEVEL",
]


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    local_archive = os.environ.get("NCES_ARCHIVE")
    if local_archive:
        print(f"Reading {local_archive}", flush=True)
        archive = Path(local_archive).read_bytes()
    else:
        print(f"Downloading {URL}", flush=True)
        with urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=180) as response:
            chunks = []
            received = 0
            while True:
                chunk = response.read(262144)
                if not chunk:
                    break
                chunks.append(chunk)
                received += len(chunk)
                if received // (1024 * 1024) != (received - len(chunk)) // (1024 * 1024):
                    print(f"Downloaded {received} bytes", flush=True)
            archive = b"".join(chunks)
    print(f"Downloaded {len(archive)} bytes", flush=True)
    with ZipFile(io.BytesIO(archive)) as zf:
        csv_name = next(name for name in zf.namelist() if name.lower().endswith(".csv"))
        text = io.TextIOWrapper(zf.open(csv_name), encoding="utf-8-sig")
        rows = []
        for source_row in csv.DictReader(text):
            row = {field.lower(): (source_row.get(field) or None) for field in FIELDS}
            row["source"] = "https://nces.ed.gov/ccd/psu_rev.asp"
            row["vintage"] = "2024-25 CCD public school universe"
            row["retrieved_at"] = retrieved_at
            rows.append(row)
    rows.sort(key=lambda row: (row.get("st") or "", row.get("ncessch") or ""))
    parts = []
    for index in range(2):
        start = (len(rows) * index) // 2
        end = (len(rows) * (index + 1)) // 2
        filename = f"nces_public_schools_2024_25_part{index + 1}.json"
        output = rows[start:end]
        (NORMALIZED / filename).write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
        parts.append({"file": "data/normalized/" + filename, "records": len(output)})
    manifest = {
        "retrieved_at": retrieved_at,
        "source": "https://nces.ed.gov/ccd/psu_rev.asp",
        "source_download": URL,
        "records": len(rows),
        "parts": parts,
        "note": "NCES Common Core of Data 2024-25 public-school universe; stable school/district IDs, names, addresses, contacts, status, type, charter flag, and grade range. No API key used.",
    }
    (RAW / "nces_public_schools_2024_25_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
