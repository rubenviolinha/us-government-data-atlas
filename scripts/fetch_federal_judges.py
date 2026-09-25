#!/usr/bin/env python3
"""Fetch the Federal Judicial Center's flat Article III judge export."""

from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

SOURCE_URL = "https://www.fjc.gov/sites/default/files/history/judges.csv"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    request = Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    raw_path = RAW / "federal-judges-fjc.csv"
    raw_path.write_bytes(payload)
    text = payload.decode("utf-8-sig")
    rows = list(csv.DictReader(text.splitlines()))
    for row in rows:
        row["source"] = SOURCE_URL
    rows.sort(key=lambda row: (row.get("Last Name", ""), row.get("First Name", ""), row.get("jid", "")))
    output = NORMALIZED / "federal_judges.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": SOURCE_URL,
        "raw_file": "data/raw/federal-judges-fjc.csv",
        "file": "data/normalized/federal_judges.json",
        "records": len(rows),
        "fields": len(rows[0]) if rows else 0,
    }
    (RAW / "federal_judges_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
