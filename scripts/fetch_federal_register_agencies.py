#!/usr/bin/env python3
"""Fetch the Federal Register's public agency catalog."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

SOURCE_URL = "https://www.federalregister.gov/api/v1/agencies.json"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    request = Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    agencies = json.loads(payload)
    (RAW / "federal-register-agencies.json").write_bytes(payload)
    agencies.sort(key=lambda row: (row.get("name") or "", row.get("short_name") or ""))
    for agency in agencies:
        agency["source"] = SOURCE_URL
    output = NORMALIZED / "federal_register_agencies.json"
    output.write_text(json.dumps(agencies, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": SOURCE_URL,
        "raw_file": "data/raw/federal-register-agencies.json",
        "file": "data/normalized/federal_register_agencies.json",
        "agencies": len(agencies),
    }
    (RAW / "federal_register_agency_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
