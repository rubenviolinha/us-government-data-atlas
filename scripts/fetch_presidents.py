#!/usr/bin/env python3
"""Fetch the National Archives' chronological list of U.S. presidents."""

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

SOURCE_URL = "https://www.archives.gov/research/census/presidents"


def iso_date(value):
    value = value.replace("Sept.", "September").replace("Aug.", "August")
    if value.lower() == "present":
        return None
    return datetime.strptime(value, "%B %d, %Y").date().isoformat()


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    request = Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    (RAW / "presidents-national-archives.html").write_bytes(payload)

    soup = BeautifulSoup(payload, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("National Archives president table was not found")
    rows = []
    for tr in table.select("tr")[1:]:
        cells = tr.find_all("td")
        if len(cells) != 2:
            continue
        name = " ".join(cells[0].get_text(" ", strip=True).split())
        dates = " ".join(cells[1].get_text(" ", strip=True).split())
        parts = re.split(r"\s*[–—-]\s*", dates, maxsplit=1)
        if len(parts) != 2:
            raise RuntimeError(f"Unrecognized presidential date range: {dates}")
        profile = cells[0].find("a")
        rows.append({
            "name": name,
            "start_date": iso_date(parts[0]),
            "end_date": iso_date(parts[1]),
            "date_text": dates,
            "profile_url": "https://www.archives.gov" + profile["href"] if profile and profile.get("href", "").startswith("/") else None,
            "source": SOURCE_URL,
        })

    output = NORMALIZED / "presidents.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": SOURCE_URL,
        "raw_file": "data/raw/presidents-national-archives.html",
        "file": "data/normalized/presidents.json",
        "presidential_service_records": len(rows),
        "distinct_names": len({row["name"] for row in rows}),
    }
    (RAW / "president_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
