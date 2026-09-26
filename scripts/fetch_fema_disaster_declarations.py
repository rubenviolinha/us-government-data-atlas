#!/usr/bin/env python3
"""Fetch FEMA's public nationwide disaster-declaration summary feed."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries.csv"


def clean(row):
    result = {}
    for key, value in row.items():
        if value == "":
            result[key] = None
        elif key in {"disasterNumber", "fyDeclared", "ihProgramDeclared", "iaProgramDeclared", "paProgramDeclared", "hmProgramDeclared", "incidentBeginDate", "incidentEndDate", "declarationDate"}:
            result[key] = value
        else:
            result[key] = value
    return result


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=900) as response:
        payload = response.read()
    rows = [clean(row) for row in csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))]
    rows.sort(key=lambda row: (row.get("disasterNumber") or "", row.get("state") or "", row.get("declarationDate") or ""))
    source = URL
    for row in rows:
        row["source"] = source
        row["retrieved_at"] = retrieved_at
    filename = "fema_disaster_declarations.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": source, "records": len(rows), "file": "data/normalized/" + filename, "note": "Nationwide FEMA disaster-declaration summary feed; public endpoint, no API key used."}
    (RAW / "fema_disaster_declarations_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
