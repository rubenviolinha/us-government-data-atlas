#!/usr/bin/env python3
"""Fetch the official 2020 Census ZCTA-to-tract relationship file."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_tract20_natl.txt"


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        text = response.read().decode("utf-8-sig")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for raw in csv.DictReader(io.StringIO(text), delimiter="|"):
        if not raw.get("GEOID_ZCTA5_20") or not raw.get("GEOID_TRACT_20"):
            continue
        rows.append({
            "zcta": raw["GEOID_ZCTA5_20"],
            "zcta_name": raw["NAMELSAD_ZCTA5_20"],
            "tract": raw["GEOID_TRACT_20"],
            "tract_name": raw["NAMELSAD_TRACT_20"],
            "zcta_land_area": int(raw["AREALAND_ZCTA5_20"] or 0),
            "zcta_water_area": int(raw["AREAWATER_ZCTA5_20"] or 0),
            "tract_land_area": int(raw["AREALAND_TRACT_20"] or 0),
            "tract_water_area": int(raw["AREAWATER_TRACT_20"] or 0),
            "land_area_part": int(raw["AREALAND_PART"] or 0),
            "water_area_part": int(raw["AREAWATER_PART"] or 0),
            "source": URL,
            "vintage": "2020 Census ZCTA-to-tract relationship file",
            "retrieved_at": retrieved_at,
        })
    rows.sort(key=lambda row: (row["zcta"], row["tract"]))
    part_size = 45000
    for index in range(0, len(rows), part_size):
        part = index // part_size + 1
        out = ROOT / "data" / "normalized" / f"zcta_tract_relationships_2020_part{part}.json"
        out.write_text(json.dumps(rows[index:index + part_size], indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.census.gov/geographies/reference-files/2020/geo/relationship-files.html",
        "vintage": "2020 Census ZCTA-to-tract relationship file",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "parts": (len(rows) + part_size - 1) // part_size,
        "raw_rows": len(text.splitlines()) - 1,
    }
    manifest_path = ROOT / "data" / "raw" / "zcta_tract_relationships_2020_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched {len(rows)} ZCTA-to-tract relationships")


if __name__ == "__main__":
    main()
