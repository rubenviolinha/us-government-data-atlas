#!/usr/bin/env python3
"""Fetch the FEC's official 2004 presidential general results workbook."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

import xlrd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www.fec.gov/documents/1628/2004pres.xls"


def clean(value):
    if value == "":
        return None
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def votes(value):
    value = clean(value)
    if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        return int(value[1:-1].replace(",", ""))
    return value if isinstance(value, (int, float)) else None


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    payload = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=120).read()
    workbook = xlrd.open_workbook(file_contents=payload)
    sheet = workbook.sheet_by_name("2004 PRES GENERAL RESULTS")
    headers = [str(v).strip().lower().replace(" ", "_").replace("#", "") if v is not None else "" for v in sheet.row_values(0)]
    rows = []
    for values in (sheet.row_values(i) for i in range(1, sheet.nrows)):
        row = {header: clean(value) for header, value in zip(headers, values) if header and clean(value) is not None}
        general_votes = votes(row.get("general_results"))
        if not row.get("fec_id") or not row.get("last_name,__first") or general_votes is None:
            continue
        rows.append({
            "fec_id": row["fec_id"], "candidate_name": row["last_name,__first"],
            "first_name": row.get("first_name"), "last_name": row.get("last_name"),
            "state": row.get("state_abbreviation"), "party": row.get("party"),
            "votes": general_votes, "vote_share": row.get("general_%"),
            "election_year": 2004, "source": URL, "source_sheet": sheet.name,
        })
    rows.sort(key=lambda row: (row["state"], -row["votes"], row["candidate_name"]))
    filename = "fec_presidential_general_2004.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": URL, "format": "legacy Excel workbook", "records": len(rows), "file": "data/normalized/" + filename}
    (RAW / "fec_presidential_general_2004_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
