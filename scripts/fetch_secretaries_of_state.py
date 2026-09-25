#!/usr/bin/env python3
"""Fetch the State Department Historian's Secretary of State roster."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

SOURCE_URL = "https://history.state.gov/departmenthistory/people/principalofficers/secretary"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    request = Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    (RAW / "secretaries-of-state-office-of-historian.html").write_bytes(payload)
    soup = BeautifulSoup(payload, "html.parser")
    rows = []
    for link in soup.select("main li a[href*='/departmenthistory/people/']"):
        parent = link.parent
        text = " ".join(parent.get_text(" ", strip=True).split())
        match = re.search(r"\((\d{4})(?:\s*[–-]\s*(\d{4}))?\)$", text)
        if not match:
            continue
        rows.append({
            "name": link.get_text(" ", strip=True),
            "start_year": int(match.group(1)),
            "end_year": int(match.group(2)) if match.group(2) else None,
            "profile_url": "https://history.state.gov" + link["href"],
            "source": SOURCE_URL,
        })
    if len(rows) < 60:
        raise RuntimeError(f"Unexpectedly low Secretary of State record count: {len(rows)}")
    rows.sort(key=lambda row: (row["start_year"], row["name"]))
    output = NORMALIZED / "secretaries_of_state.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": SOURCE_URL,
        "raw_file": "data/raw/secretaries-of-state-office-of-historian.html",
        "file": "data/normalized/secretaries_of_state.json",
        "records": len(rows),
        "distinct_names": len({row["name"] for row in rows}),
        "scope_note": "The source explicitly excludes designated acting Secretaries of State when the office was vacant.",
    }
    (RAW / "secretary_of_state_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
