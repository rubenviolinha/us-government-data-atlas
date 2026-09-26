#!/usr/bin/env python3
"""Fetch public Census ACS 2024 variable metadata for the atlas profile tables."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
BASE = "https://api.census.gov/data/2024/acs/acs5/groups/"
TABLES = ("B01001", "B15003", "B17001", "B19013", "B25001", "B02001")


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    sources = []
    for table in TABLES:
        source = BASE + table + ".json"
        sources.append(source)
        with urlopen(Request(source, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=60) as response:
            payload = json.load(response)
        for variable, metadata in payload.get("variables", {}).items():
            if not variable.startswith(table + "_"):
                continue
            row = {"variable": variable, "table": table, "label": metadata.get("label"), "concept": metadata.get("concept"), "predicate_type": metadata.get("predicateType"), "predicate_only": metadata.get("predicateOnly"), "group": metadata.get("group"), "limit": metadata.get("limit"), "source": source, "vintage": "2024 ACS 5-year", "retrieved_at": retrieved_at}
            rows.append(row)
    rows.sort(key=lambda row: row["variable"])
    filename = "acs_profile_variables_2024.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "sources": sources, "format": "Census API group metadata JSON", "tables": list(TABLES), "records": len(rows), "file": "data/normalized/" + filename, "note": "Public ACS 2024 5-year variable labels and metadata; no API key used for group metadata."}
    (RAW / "acs_profile_variables_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
