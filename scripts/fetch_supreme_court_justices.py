#!/usr/bin/env python3
"""Fetch the Supreme Court's official historical justice roster."""

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

SOURCE_URL = "https://www.supremecourt.gov/about/members_text.aspx"


def parse_date(value):
    value = re.sub(r"\([a-z]+\)\s*", "", value, flags=re.I).replace("*", "").strip()
    if not value:
        return None
    value = re.sub(r"^(\w+ \d{1,2}) (\d{4})$", r"\1, \2", value)
    value = re.sub(r",\s*", ", ", value)
    return datetime.strptime(value, "%B %d, %Y").date().isoformat()


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    request = Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    (RAW / "supreme-court-justices.html").write_bytes(payload)
    soup = BeautifulSoup(payload, "html.parser")
    rows = []
    for heading in soup.select("div > span"):
        role = heading.get_text(" ", strip=True)
        if role not in {"Chief Justices", "Associate Justices"}:
            continue
        table = heading.find_parent("div").find_next("table")
        for tr in table.select("tr")[1:]:
            cells = tr.find_all("td")
            if len(cells) != 5:
                continue
            rows.append({
                "name": " ".join(cells[0].get_text(" ", strip=True).split()),
                "role": "chief" if role == "Chief Justices" else "associate",
                "state_appointed_from": " ".join(cells[1].get_text(" ", strip=True).split()),
                "appointed_by_president": " ".join(cells[2].get_text(" ", strip=True).split()),
                "oath_date": parse_date(cells[3].get_text(" ", strip=True)),
                "service_terminated_date": parse_date(cells[4].get_text(" ", strip=True)),
                "source": SOURCE_URL,
            })
    if len(rows) < 100:
        raise RuntimeError(f"Unexpectedly low justice record count: {len(rows)}")
    rows.sort(key=lambda row: (row["oath_date"] or "", row["name"], row["role"]))
    output = NORMALIZED / "supreme_court_justices.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": SOURCE_URL,
        "raw_file": "data/raw/supreme-court-justices.html",
        "file": "data/normalized/supreme_court_justices.json",
        "records": len(rows),
        "chief_records": sum(row["role"] == "chief" for row in rows),
        "associate_records": sum(row["role"] == "associate" for row in rows),
    }
    (RAW / "supreme_court_justice_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
