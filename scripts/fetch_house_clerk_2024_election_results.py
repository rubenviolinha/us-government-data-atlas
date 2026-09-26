#!/usr/bin/env python3
"""Extract official 2024 federal candidate vote totals from the House Clerk PDF."""

from datetime import datetime, timezone
import io
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
URL = "https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf"
PARTIES = (
    "Party for Socialism and Liberation", "No Party Preference", "American Solidarity",
    "Working Families", "Peace and Freedom", "Conservative", "Democratic", "Democrat",
    "Republican", "Independent", "Libertarian", "Constitution", "Green", "American",
    "Aurora", "Independence", "Petition", "United Utah", "Unaffiliated", "Natural Law",
    "New Alliance", "Write-in",
)
STATUS_ROWS = {"Write-in", "Blank", "Scattering", "Void", "Under Votes", "Over Votes"}
PARTY_RE = re.compile(r",\s*(" + "|".join(re.escape(x) for x in sorted(PARTIES, key=len, reverse=True)) + r")\s*$", re.I)
STATE_RE = re.compile(r"^[A-Z][A-Z .&'\-]+(?:—Continued)?$")
NUMBER_RE = re.compile(r"^\s*[\d,]+\s*$")


def parse(payload):
    reader = PdfReader(io.BytesIO(payload))
    rows = []
    state = office = district = None
    pending = []
    for page_number, page in enumerate(reader.pages[2:], 3):
        for raw in (page.extract_text() or "").splitlines():
            original = raw.replace("\xa0", " ").strip()
            if not original:
                continue
            if NUMBER_RE.match(original) and pending:
                candidate = pending.pop(0)
                rows.append({**candidate, "votes": int(original.replace(",", ""))})
                continue
            line = original
            if STATE_RE.match(line) and not line.startswith(("FOR ", "STATISTICS", "Recapitulation", "Title", "Total")) and "Continued" not in line:
                state, office, district, pending = line, None, None, []
                continue
            match = re.match(r"FOR UNITED STATES (SENATOR|REPRESENTATIVE)(?:—Continued)?", line)
            if match:
                office, district, pending = match.group(1).lower(), None, []
                continue
            if line.startswith("FOR RESIDENT COMMISSIONER"):
                office, district, pending = "resident_commissioner", None, []
                continue
            if line.startswith("FOR DELEGATE"):
                office, district, pending = "delegate", None, []
                continue
            if office is None or line.startswith("Recapitulation"):
                pending = [] if line.startswith("Recapitulation") else pending
                continue
            district_match = re.match(r"^(\d+|AT LARGE|At large)\.?\s*(.*)$", line)
            if district_match and district_match.group(2):
                district = district_match.group(1).lower().replace(" ", "_")
                line = district_match.group(2).strip()
            clean = re.sub(r"\.{3,}|…+", " ", line).strip()
            party_match = PARTY_RE.search(clean)
            if party_match:
                name = clean[:party_match.start()].strip(" .")
                party = party_match.group(1)
                pending.append({
                    "state": state,
                    "office": office,
                    "district": district,
                    "candidate_name": name,
                    "party": party,
                    "record_type": "ballot_status" if party in STATUS_ROWS else "candidate",
                    "source_page": page_number,
                })
                continue
            if clean in STATUS_ROWS:
                pending.append({
                    "state": state,
                    "office": office,
                    "district": district,
                    "candidate_name": clean,
                    "party": clean,
                    "record_type": "ballot_status",
                    "source_page": page_number,
                })
    return rows


def main():
    payload = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=120).read()
    rows = parse(payload)
    for index, row in enumerate(rows, 1):
        row.update({"election_year": 2024, "source": URL, "record_id": f"house-clerk-2024-{index:04d}"})
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "house_clerk_statistics_2024.pdf").write_bytes(payload)
    filename = "fec_congressional_results_2024.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": URL, "format": "Official House Clerk PDF", "records": len(rows), "file": "data/normalized/" + filename, "note": "Official candidate-level vote totals for U.S. Senate, Representative, Resident Commissioner, and Delegate contests; extracted from the Clerk's published 2024 election statistics; no API key used."}
    (RAW / "house_clerk_statistics_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
