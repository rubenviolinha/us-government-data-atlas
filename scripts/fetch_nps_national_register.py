#!/usr/bin/env python3
"""Fetch the NPS National Register of Historic Places listed-properties CSV."""

from datetime import datetime, timezone
import csv
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
URL = "https://www.nps.gov/common/uploads/sortable_dataset/nationalregister/53699964-0893-68AA-5273CB1C614B8BB3/nri-national-register-listed20260522.csv"
FIELDS = [
    "Ref#", "Prefix", "Property Name", "State", "County", "City ", "Street & Number",
    "Status", "Request Type", "Restricted Address", "Acreage of Property",
    "Area of Significance", "Category of Property", "External Link",
    "Level of Significance - International", "Level of Significance - National",
    "Level of Significance - State", "Level of Significance - Local",
    "Level of Significance - Not Indicated", "Listed Date", "NHL Designated Date",
    "Other Names", "Park Name", "Property ID",
]


def key(field):
    return field.lower().replace(" ", "_").replace("#", "_number").strip("_")


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    local_file = os.environ.get("NPS_ARCHIVE")
    if local_file:
        payload = Path(local_file).read_bytes()
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
            payload = b"".join(chunks)
    rows = []
    for source_row in csv.DictReader(io.TextIOWrapper(io.BytesIO(payload), encoding="cp1252")):
        row = {key(field): (source_row.get(field) or None) for field in FIELDS}
        row["source"] = "https://www.nps.gov/subjects/nationalregister/database-research.htm"
        row["vintage"] = "NPS National Register listed properties through 2026-05-22"
        row["retrieved_at"] = retrieved_at
        rows.append(row)
    rows.sort(key=lambda row: (row.get("state") or "", row.get("ref_number") or ""))
    parts = []
    for index in range(4):
        start = (len(rows) * index) // 4
        end = (len(rows) * (index + 1)) // 4
        filename = f"nps_national_register_listed_2026_part{index + 1}.json"
        output = rows[start:end]
        (NORMALIZED / filename).write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
        parts.append({"file": "data/normalized/" + filename, "records": len(output)})
    manifest = {
        "retrieved_at": retrieved_at,
        "source": "https://www.nps.gov/subjects/nationalregister/database-research.htm",
        "source_download": URL,
        "records": len(rows),
        "parts": parts,
        "note": "NPS National Register of Historic Places listed-properties public CSV; split into four repository-safe JSON parts."
    }
    (RAW / "nps_national_register_listed_2026_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
