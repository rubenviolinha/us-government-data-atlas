#!/usr/bin/env python3
"""Extract state and territory election-office sections from the FEC directory PDF."""

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
URL = "https://www.fec.gov/resources/cms-content/documents/cfsded.pdf"
URL_RE = re.compile(r"https?://[^\s*]+")
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?1[-. ]?)?(?:\(?\d{3}\)?[-. ]?)\d{3}[-. ]\d{4}")

def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=300).read()
    (RAW / "fec_state_election_directory_2025.pdf").write_bytes(payload)
    names = [(row["name"], row["state_fips"]) for row in json.loads((NORMALIZED / "states.json").read_text(encoding="utf-8"))]
    headings = {name.upper(): name for name, _ in names}
    headings["VIRGIN ISLANDS"] = "U.S. Virgin Islands"
    pages = PdfReader(io.BytesIO(payload)).pages
    sections = {name: {"page_start": None, "pages": []} for name, _ in names}
    current = None
    for number, page in enumerate(pages, start=1):
        text = page.extract_text() or ""
        for line in (line.strip() for line in text.splitlines()):
            key = re.sub(r"\s+\(Continued\)$", "", line, flags=re.I).strip().upper()
            if key in headings:
                current = headings[key]
                if sections[current]["page_start"] is None:
                    sections[current]["page_start"] = number
                break
        if current:
            sections[current]["pages"].append((number, text))
    rows = []
    for name, fips in names:
        section = sections[name]
        text = "\n\n".join(page_text.strip() for _, page_text in section["pages"] if page_text.strip())
        rows.append({"state_name": name, "state_fips": fips, "page_start": section["page_start"], "page_count": len(section["pages"]), "section_available": bool(text), "urls": sorted(set(URL_RE.findall(text))), "emails": sorted(set(EMAIL_RE.findall(text))), "phones": sorted(set(PHONE_RE.findall(text))), "section_text": text, "source": URL, "source_vintage": "FEC Combined Federal/State Disclosure and Election Directory, revised July 2025", "retrieved_at": retrieved_at})
    filename = "fec_state_election_directory_2025.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": URL, "format": "PDF", "records": len(rows), "file": "data/normalized/" + filename, "note": "State and territory election/disclosure office sections preserved with extracted contact fields and source text; no API key used."}
    (RAW / "fec_state_election_directory_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
