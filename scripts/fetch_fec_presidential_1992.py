#!/usr/bin/env python3
"""Extract text-based 1992 presidential general rows from the official FEC PDF."""

from datetime import datetime, timezone
import hashlib, json, re
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]; RAW = ROOT / "data" / "raw"; NORMALIZED = ROOT / "data" / "normalized"
PDF = "https://www.fec.gov/documents/1552/federalelections92.pdf"
LOCAL = ROOT / "tmp" / "pdfs" / "federalelections92.pdf"
STATES = {row["name"].upper(): row.get("abbr") for row in json.loads((NORMALIZED / "states.json").read_text())}
STATES.update({"DISTRICT OF COLUMBIA": "DC", "VIRGIN ISLANDS": "VI", "PUERTO RICO": "PR", "GUAM": "GU", "AMERICAN SAMOA": "AS"})


def main():
    RAW.mkdir(parents=True, exist_ok=True); NORMALIZED.mkdir(parents=True, exist_ok=True)
    rows = []; state = None
    with pdfplumber.open(LOCAL) as pdf:
        for page in pdf.pages[19:39]:
            for raw in (page.extract_text() or "").splitlines():
                line = " ".join(raw.split())
                upper = line.upper()
                if upper in STATES:
                    state = STATES[upper]; continue
                match = re.match(r"^(.*?)\s+([0-9][0-9,]*)\s+([.]?[0-9]{1,3})$", line)
                if not state or not match or "TOTAL VOTE" in upper or "CANDIDATE NAME" in upper:
                    continue
                label, votes, pct = match.groups()
                if label.lower().startswith(("write-in", "scattered")):
                    continue
                parts = label.rsplit(" ", 1)
                candidate = parts[0].strip(); party = parts[1].strip() if len(parts) == 2 else ""
                if not candidate or not any(ch.isalpha() for ch in candidate):
                    continue
                key = f"1992|{state}|{candidate}|{party}"
                rows.append({"fec_id": "LEGACY-" + hashlib.sha1(key.encode()).hexdigest()[:16].upper(), "candidate_name": candidate, "party_label": party, "state": state, "votes": int(votes.replace(",", "")), "vote_share": float(pct.replace(".", "0.", 1)) if pct.startswith(".") else float(pct), "election_year": 1992, "source": PDF, "source_page_range": "20-39", "id_type": "synthetic legacy record ID"})
    unique = {(row["fec_id"]): row for row in rows}
    rows = sorted(unique.values(), key=lambda row: (row["state"], -row["votes"], row["candidate_name"]))
    filename = "fec_presidential_general_1992.json"; (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": PDF, "format": "OCR text extracted from official PDF", "records": len(rows), "file": "data/normalized/" + filename, "note": "Synthetic IDs and preserved source-page metadata are used because the 1992 PDF predates modern FEC candidate IDs."}
    (RAW / "fec_presidential_general_1992_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"); print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
