#!/usr/bin/env python3
"""Fetch vice-presidential terms from the Library of Congress research guide."""

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

SOURCE_URL = "https://guides.loc.gov/vice-presidents-portraits/alphabetical"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    request = Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    (RAW / "vice-presidents-library-of-congress.html").write_bytes(payload)
    soup = BeautifulSoup(payload, "html.parser")
    rows = []
    for paragraph in soup.select("p"):
        link = paragraph.find("a")
        if not link:
            continue
        text = " ".join(paragraph.get_text(" ", strip=True).split())
        match = re.match(r"(.+?)\s*\((\d{4})(?:\s*-\s*(\d{4})?\s*)?\)$", text)
        if not match:
            continue
        rows.append({
            "name": match.group(1).strip(),
            "start_year": int(match.group(2)),
            "end_year": int(match.group(3)) if match.group(3) else None,
            "profile_url": link.get("href"),
            "source": SOURCE_URL,
        })
    if len(rows) < 40:
        raise RuntimeError(f"Unexpectedly low vice-president record count: {len(rows)}")
    rows.sort(key=lambda row: (row["start_year"], row["name"]))
    output = NORMALIZED / "vice_presidents.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": SOURCE_URL,
        "raw_file": "data/raw/vice-presidents-library-of-congress.html",
        "file": "data/normalized/vice_presidents.json",
        "records": len(rows),
        "distinct_names": len({row["name"] for row in rows}),
    }
    (RAW / "vice_president_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
