#!/usr/bin/env python3
"""Fetch the official 2020 Census tract-to-PUMA relationship file."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/2020_Census_Tract_to_2020_PUMA.txt"


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    text = urlopen(request, timeout=120).read().decode("utf-8-sig")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for raw in csv.DictReader(io.StringIO(text)):
        state = (raw.get("STATEFP") or "").strip()
        county = (raw.get("COUNTYFP") or "").strip()
        tract_code = (raw.get("TRACTCE") or "").strip()
        puma_code = (raw.get("PUMA5CE") or "").strip()
        if not (state and county and tract_code and puma_code):
            continue
        rows.append({
            "state": state,
            "county": county,
            "tract_code": tract_code,
            "tract": state + county + tract_code,
            "puma_code": puma_code,
            "puma": state + puma_code,
            "source": URL,
            "vintage": "2020 Census tract-to-PUMA relationship file",
            "retrieved_at": retrieved_at,
        })
    rows.sort(key=lambda row: (row["tract"], row["puma"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    filename = "tract_puma_relationships_2020.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.census.gov/geographies/reference-files/2020/geo/relationship-files.html",
        "format": "Census relationship CSV",
        "vintage": "2020 Census tract-to-PUMA relationship file",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "raw_rows": len(text.splitlines()) - 1,
        "file": "data/normalized/" + filename,
        "note": "Keyless tract-to-PUMA relationship keyed by 2020 Census GEOIDs.",
    }
    (RAW / "tract_puma_relationships_2020_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
