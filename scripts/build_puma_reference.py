#!/usr/bin/env python3
"""Build a deduplicated PUMA reference table from Census relationships."""

from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"; RAW = ROOT / "data" / "raw"


def main():
    relationships = json.loads((DATA / "puma_zcta_relationships_2020.json").read_text(encoding="utf-8"))
    fields = ("OID_PUMA5_20", "GEOID_PUMA5_20", "NAMELSAD_PUMA5_20", "AREALAND_PUMA5_20", "AREAWATER_PUMA5_20", "MTFCC_PUMA5_20", "FUNCSTAT_PUMA5_20")
    rows = [{field: row[field] for field in fields} for row in {row["GEOID_PUMA5_20"]: row for row in relationships}.values()]
    rows.sort(key=lambda row: row["GEOID_PUMA5_20"])
    filename = "pumas_2020.json"
    (DATA / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": "https://www2.census.gov/geo/docs/maps-data/data/rel2020/puma520/tab20_puma520_zcta520_natl.txt", "format": "Derived Census relationship reference", "records": len(rows), "file": "data/normalized/" + filename, "note": "Deduplicated PUMA reference records derived from the official Census PUMA-ZCTA relationship file; no API key used."}
    (RAW / "pumas_2020_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
