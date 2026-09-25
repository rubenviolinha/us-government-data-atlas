#!/usr/bin/env python3
"""Fetch official FEC 2000 presidential general results (legacy workbook)."""

from datetime import datetime, timezone
import hashlib, json
from pathlib import Path
from urllib.request import Request, urlopen
import xlrd

ROOT = Path(__file__).resolve().parents[1]; RAW = ROOT / "data" / "raw"; NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www.fec.gov/documents/1612/2000presge.xls"


def main():
    RAW.mkdir(parents=True, exist_ok=True); NORMALIZED.mkdir(parents=True, exist_ok=True)
    workbook = xlrd.open_workbook(file_contents=urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=120).read())
    sheet = workbook.sheet_by_name("Master By State")
    rows = []
    for i in range(1, sheet.nrows):
        state, candidate, party, votes, _combined = sheet.row_values(i)
        if not state or not candidate or not party or not isinstance(votes, (int, float)) or str(candidate).lower() in {"scattered", "total"}:
            continue
        state = str(state).strip(); candidate = str(candidate).strip(); party = str(party).strip()
        key = f"2000|{state}|{candidate}|{party}"
        rows.append({"fec_id": "LEGACY-" + hashlib.sha1(key.encode()).hexdigest()[:16].upper(), "candidate_name": candidate, "state": state, "party": party, "votes": int(votes), "election_year": 2000, "source": URL, "source_sheet": sheet.name, "id_type": "synthetic legacy record ID"})
    rows.sort(key=lambda row: (row["state"], -row["votes"], row["candidate_name"]))
    filename = "fec_presidential_general_2000.json"; (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": URL, "format": "legacy Excel workbook", "records": len(rows), "file": "data/normalized/" + filename, "note": "The legacy 2000 workbook has no modern FEC candidate IDs; stable synthetic IDs are included."}
    (RAW / "fec_presidential_general_2000_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"); print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
