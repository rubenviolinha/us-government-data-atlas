#!/usr/bin/env python3
"""Extract 1984 presidential results from the official FEC historical PDF."""

from datetime import datetime, timezone
import difflib, hashlib, json, re
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
PDF = "https://www.fec.gov/documents/1548/federalelections84.pdf"
LOCAL = ROOT / "tmp" / "pdfs" / "federalelections84.pdf"
STATES = {row["name"].upper(): row.get("abbr") for row in json.loads((NORMALIZED / "states.json").read_text())}
STATES.update({"DISTRICT OF COLUMBIA": "DC", "VIRGIN ISLANDS": "VI", "PUERTO RICO": "PR", "GUAM": "GU", "AMERICAN SAMOA": "AS"})
# A few state headings are damaged by the source PDF's text layer.
STATES.update({"HAWALL": "HI", "HAWAII": "HI", "OMO": "OH", "OHIO": "OH"})


def main():
    RAW.mkdir(parents=True, exist_ok=True); NORMALIZED.mkdir(parents=True, exist_ok=True)
    rows, state = [], None
    with pdfplumber.open(LOCAL) as pdf:
        for page in pdf.pages[7:19]:
            for raw in (page.extract_text() or "").splitlines():
                line = " ".join(raw.split()); upper = line.upper()
                if line and not any(ch.isdigit() for ch in line) and len(line) > 3 and "," not in line and "CANDIDATE" not in upper and "PARTY" not in upper:
                    match = difflib.get_close_matches(upper, STATES, n=1, cutoff=.72)
                    if match:
                        state = STATES[match[0]]
                        continue
                match = re.match(r"^(.*?)\s+([0-9][0-9, '’]*)\s+([0-9]+(?:\.[0-9]+)?)$", line)
                if not state or not match or "TOTAL VOTE" in upper or line.lower().startswith(("write-in", "total")):
                    continue
                label, votes, pct = match.groups()
                digits = re.sub(r"\D", "", votes)
                if not digits or not any(ch.isalpha() for ch in label):
                    continue
                key = f"1984|{state}|{label}|{digits}"
                rows.append({"fec_id": "LEGACY-" + hashlib.sha1(key.encode()).hexdigest()[:16].upper(), "candidate_label": label.strip(), "state": state, "votes": int(digits), "vote_share": float(pct), "election_year": 1984, "source": PDF, "source_page_range": "8-19", "id_type": "synthetic legacy record ID"})
    rows = list({row["fec_id"]: row for row in rows}.values())
    rows.sort(key=lambda row: (row["state"], -row["votes"], row["candidate_label"]))
    filename = "fec_presidential_general_1984.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": PDF, "format": "text extracted from official PDF", "records": len(rows), "file": "data/normalized/" + filename, "note": "Synthetic IDs and source-page metadata are used because the 1984 PDF predates modern FEC candidate IDs; OCR artifacts are preserved."}
    (RAW / "fec_presidential_general_1984_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
