#!/usr/bin/env python3
"""Fetch the official FEC 2024 committee master bulk file without an API key."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
URL = "https://www.fec.gov/files/bulk-downloads/2024/cm24.zip"
FIELDS = [
    "committee_id", "committee_name", "treasurer_name", "street_1", "street_2", "city",
    "state", "zip_code", "designation", "committee_type", "party_affiliation", "filing_frequency",
    "organization_type", "connected_organization_name", "candidate_id",
]


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=300) as response:
        payload = response.read()
    with ZipFile(io.BytesIO(payload)) as archive:
        filename = next(name for name in archive.namelist() if name.endswith(".txt"))
        rows = []
        for values in csv.reader(io.TextIOWrapper(archive.open(filename), encoding="latin-1"), delimiter="|"):
            if len(values) != len(FIELDS):
                continue
            row = dict(zip(FIELDS, values))
            row.update({"cycle": 2024, "source": URL})
            rows.append(row)
    rows.sort(key=lambda row: row["committee_id"])
    (NORMALIZED / "fec_committee_master_2024.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": URL,
        "format": "FEC committee master pipe-delimited text inside ZIP",
        "records": len(rows),
        "file": "data/normalized/fec_committee_master_2024.json",
        "note": "Official bulk file; no FEC API key used."
    }
    (RAW / "fec_committee_master_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
