#!/usr/bin/env python3
"""Fetch the official FEC 2024 candidate master bulk file without an API key."""

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
URL = "https://www.fec.gov/files/bulk-downloads/2024/cn24.zip"
FIELDS = [
    "candidate_id", "candidate_name", "party_affiliation", "election_year", "office_state",
    "office", "district", "incumbent_challenger", "candidate_status", "principal_committee_id",
    "street_1", "street_2", "city", "state", "zip_code",
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
            row["election_year"] = int(row["election_year"]) if row["election_year"].isdigit() else row["election_year"]
            row.update({"cycle": 2024, "source": URL})
            rows.append(row)
    rows.sort(key=lambda row: row["candidate_id"])
    (NORMALIZED / "fec_candidate_master_2024.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": URL,
        "format": "FEC candidate master pipe-delimited text inside ZIP",
        "records": len(rows),
        "file": "data/normalized/fec_candidate_master_2024.json",
        "note": "Official bulk file; no FEC API key used."
    }
    (RAW / "fec_candidate_master_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
