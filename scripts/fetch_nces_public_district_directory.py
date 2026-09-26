#!/usr/bin/env python3
"""Fetch the NCES Common Core of Data 2024-25 public LEA universe."""

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
URL = "https://nces.ed.gov/ccd/Data/zip/ccd_lea_029_2425_w_0a_051425.zip"
FIELDS = [
    "SCHOOL_YEAR", "LEAID", "ST_LEAID", "LEA_NAME", "STATENAME", "ST",
    "MCITY", "MSTATE", "MZIP", "LSTREET1", "LCITY", "LSTATE", "LZIP",
    "PHONE", "WEBSITE", "SY_STATUS_TEXT", "LEA_TYPE_TEXT", "CHARTER_LEA_TEXT",
    "GSLO", "GSHI", "LEVEL", "OPERATIONAL_SCHOOLS",
]


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    local_archive = os.environ.get("NCES_ARCHIVE")
    if local_archive:
        archive = Path(local_archive).read_bytes()
    else:
        print(f"Downloading {URL}", flush=True)
        with urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=180) as response:
            chunks = []
            while True:
                chunk = response.read(262144)
                if not chunk:
                    break
                chunks.append(chunk)
            archive = b"".join(chunks)
    with ZipFile(io.BytesIO(archive)) as zf:
        csv_name = next(name for name in zf.namelist() if name.lower().endswith(".csv"))
        text = io.TextIOWrapper(zf.open(csv_name), encoding="utf-8-sig")
        rows = []
        for source_row in csv.DictReader(text):
            row = {field.lower(): (source_row.get(field) or None) for field in FIELDS}
            row["source"] = "https://nces.ed.gov/ccd/pau_rev.asp"
            row["vintage"] = "2024-25 CCD public LEA universe"
            row["retrieved_at"] = retrieved_at
            rows.append(row)
    rows.sort(key=lambda row: (row.get("st") or "", row.get("leaid") or ""))
    filename = "nces_public_districts_2024_25.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": "https://nces.ed.gov/ccd/pau_rev.asp",
        "source_download": URL,
        "records": len(rows),
        "file": "data/normalized/" + filename,
        "note": "NCES Common Core of Data 2024-25 public local education agency universe; no API key used.",
    }
    (RAW / "nces_public_districts_2024_25_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
