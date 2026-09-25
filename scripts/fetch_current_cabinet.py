#!/usr/bin/env python3
"""Fetch the White House's current Cabinet roster without an API key."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
SOURCE_URL = "https://www.whitehouse.gov/administration/cabinet/"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with urlopen(Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=120) as response:
        payload = response.read()
    RAW.mkdir(parents=True, exist_ok=True)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    (RAW / "white-house-cabinet.html").write_bytes(payload)
    soup = BeautifulSoup(payload, "html.parser")
    records = []
    for heading in soup.select("h2"):
        name = " ".join(heading.get_text(" ", strip=True).split())
        role = heading.find_next("h3")
        if not name or not role:
            continue
        title = " ".join(role.get_text(" ", strip=True).split())
        if name.startswith("Subscribe") or "Newsletter" in title:
            continue
        image = heading.find_next("img")
        records.append({"name": name, "title": title, "profile_image_url": image.get("src") if image else None, "source": SOURCE_URL, "retrieved_at": retrieved_at})
    records = sorted({(row["name"], row["title"]): row for row in records}.values(), key=lambda row: (row["title"], row["name"]))
    if len(records) < 15:
        raise RuntimeError(f"Unexpectedly low Cabinet record count: {len(records)}")
    output = NORMALIZED / "current_cabinet_white_house.json"
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": SOURCE_URL, "file": "data/normalized/current_cabinet_white_house.json", "records": len(records)}
    (RAW / "white-house-cabinet-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
