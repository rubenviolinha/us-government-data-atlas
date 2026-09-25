#!/usr/bin/env python3
"""Extract the FEC's 2024 presidential general-ballot candidate matrix."""

from datetime import datetime, timezone
import io
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
URL = "https://www.fec.gov/resources/cms-content/documents/2024presgecands.pdf"
STATES = {row["abbr"]: row for row in json.loads((NORMALIZED / "states.json").read_text(encoding="utf-8"))}

def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300).read()
    (RAW / "fec_2024_presidential_ballots.pdf").write_bytes(payload)
    rows = []
    with pdfplumber.open(io.BytesIO(payload)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if not tables:
                continue
            table = tables[0]
            if not table:
                continue
            headers = [str(value or "").strip() for value in table[0]]
            candidate_start = 2 if headers[:2] == ["STATE", "ELECTORAL VOTES"] else 1
            for values in table[1:]:
                state_abbr = str(values[0] or "").strip()
                if state_abbr not in STATES:
                    continue
                for index in range(candidate_start, min(len(headers), len(values))):
                    candidate = headers[index]
                    marker = str(values[index] or "").strip()
                    if not candidate or candidate in {"NONE OF THESE", "CANDIDATES", "BALLOT TOTAL"} or not marker.startswith("X"):
                        continue
                    party_match = re.search(r"\(([^)]+)\)", marker)
                    rows.append({"state_abbreviation": state_abbr, "state_name": STATES[state_abbr]["name"], "candidate_label": candidate, "party_marker": party_match.group(1) if party_match else None, "ballot_marker": marker, "election_year": 2024, "source_page": page_number, "source": URL, "retrieved_at": retrieved_at})
    rows.sort(key=lambda row: (row["state_abbreviation"], row["candidate_label"], row["source_page"]))
    filename = "fec_presidential_ballot_candidates_2024.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": URL, "format": "PDF matrix", "records": len(rows), "file": "data/normalized/" + filename, "note": "Official FEC compilation of presidential candidates on 2024 general-election ballots; no API key used."}
    (RAW / "fec_2024_presidential_ballots_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
