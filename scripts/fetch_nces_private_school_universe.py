#!/usr/bin/env python3
"""Fetch the NCES 2023-24 Private School Universe Survey public-use file."""

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
URL = "https://nces.ed.gov/surveys/pss/zip/pss2324_pu_csv.zip"
FIELDS = [
    "PPIN", "PINST", "PADDRS", "PCITY", "PSTABB", "PZIP", "PZIP4", "PPHONE",
    "PCNTY", "PCNTNM", "PL_ADD", "PL_CIT", "PL_STABB", "PL_ZIP", "PL_ZIP4",
    "REGION", "PSTANSI", "ULOCALE24", "LATITUDE24", "LONGITUDE24", "SLDLST24",
    "SLDUST24", "STCD24", "LOGR2024", "HIGR2024", "FRAME", "TYPOLOGY", "RELIG",
    "ORIENT", "DIOCESE", "LEVEL", "LEVEL2", "NUMSTUDS", "SIZE", "NUMTEACH",
    "UCOMMTYP", "MALES", "P_INDIAN", "P_ASIAN", "P_PACIFIC", "P_HISP", "P_WHITE",
    "P_BLACK", "P_TR", "STTCH_RT", "LEVEL3", "GRADE2", "LEVEL4",
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
            row["source"] = "https://nces.ed.gov/surveys/pss/pssdata.asp"
            row["vintage"] = "2023-24 PSS public-use file"
            row["retrieved_at"] = retrieved_at
            rows.append(row)
    rows.sort(key=lambda row: (row.get("pstabb") or "", row.get("ppin") or ""))
    filename = "nces_private_schools_2023_24.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": "https://nces.ed.gov/surveys/pss/pssdata.asp",
        "source_download": URL,
        "records": len(rows),
        "file": "data/normalized/" + filename,
        "note": "NCES Private School Universe Survey 2023-24 public-use CSV; identifiers, addresses, geography, enrollment, staffing, school characteristics, and selected demographic percentages. No API key used.",
    }
    (RAW / "nces_private_schools_2023_24_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
