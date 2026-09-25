#!/usr/bin/env python3
"""Fetch open historical and current congressional member records."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

BASE = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/"
FILES = ["legislators-current.yaml", "legislators-historical.yaml"]


def fetch(name):
    request = Request(BASE + name, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        return response.read()


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    people = {}
    manifests = []
    for name in FILES:
        payload = fetch(name)
        (RAW / name).write_bytes(payload)
        records = yaml.safe_load(payload)
        for record in records:
            key = record.get("id", {}).get("bioguide") or record.get("name", {}).get("official_full")
            if not key:
                continue
            existing = people.setdefault(key, {"id": record.get("id", {}), "name": record.get("name", {}), "bio": record.get("bio", {}), "terms": []})
            existing["terms"].extend(record.get("terms", []))
            for field in ("id", "name", "bio"):
                existing[field].update(record.get(field, {}))
        manifests.append({"source": BASE + name, "path": "data/raw/" + name, "records": len(records)})
    normalized = sorted(people.values(), key=lambda person: (person.get("name", {}).get("last", ""), person.get("name", {}).get("first", "")))
    (NORMALIZED / "congressional_legislators.json").write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    term_count = sum(len(person["terms"]) for person in normalized)
    manifest = {"retrieved_at": retrieved_at, "sources": manifests, "people": len(normalized), "terms": term_count, "file": "data/normalized/congressional_legislators.json"}
    (RAW / "legislator_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
