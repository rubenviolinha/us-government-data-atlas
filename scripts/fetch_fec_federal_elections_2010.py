#!/usr/bin/env python3
"""Fetch the official FEC 2010 House and Senate results workbook."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen
import xlrd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"; NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www.fec.gov/documents/1677/results10.xls"
SHEET = "2010 US House & Senate Results"


def clean(value):
    if value == "": return None
    if isinstance(value, float) and value.is_integer(): return int(value)
    return value


def main():
    payload = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300).read()
    sheet = xlrd.open_workbook(file_contents=payload).sheet_by_name(SHEET)
    headers = [str(value).strip().lower().replace(" ", "_").replace("#", "") if value is not None else "" for value in sheet.row_values(0)]
    rows = []
    for values in (sheet.row_values(i) for i in range(1, sheet.nrows)):
        row = {header: clean(value) for header, value in zip(headers, values) if header and clean(value) is not None}
        fec_id = str(row.get("fec_id", ""))
        candidate = row.get("candidate_name_(last,_first)")
        if not fec_id or fec_id.lower() == "n/a" or not candidate or str(candidate).lower() in {"party votes:", "district votes:"}:
            continue
        district = str(row.get("district", ""))
        row.update({"candidate_name": candidate, "d": district, "general_votes": row.get("general"), "general_vote_share": row.get("general_%"), "election_year": 2010, "office": "senate" if district.upper() == "S" else "house", "source": URL, "source_sheet": SHEET})
        rows.append(row)
    rows.sort(key=lambda row: (row["office"], str(row.get("state_abbreviation", "")), str(row.get("d", "")), row["fec_id"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    filename = "fec_federal_elections_2010.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": URL, "format": "legacy Excel workbook", "records": len(rows), "file": "data/normalized/" + filename, "note": "Official certified federal election compilation; no API key used."}
    (RAW / "fec_federal_elections_2010_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
