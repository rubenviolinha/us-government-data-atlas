#!/usr/bin/env python3
"""Fetch the official 2020 Census ZCTA-to-place relationship file."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_place20_natl.txt"


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        text = response.read().decode("utf-8-sig")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for raw in csv.DictReader(io.StringIO(text), delimiter="|"):
        if not raw.get("GEOID_ZCTA5_20") or not raw.get("GEOID_PLACE_20"):
            continue
        rows.append({
            "zcta": raw["GEOID_ZCTA5_20"],
            "zcta_name": raw["NAMELSAD_ZCTA5_20"],
            "place": raw["GEOID_PLACE_20"],
            "place_name": raw["NAMELSAD_PLACE_20"],
            "zcta_land_area": int(raw["AREALAND_ZCTA5_20"] or 0),
            "zcta_water_area": int(raw["AREAWATER_ZCTA5_20"] or 0),
            "place_land_area": int(raw["AREALAND_PLACE_20"] or 0),
            "place_water_area": int(raw["AREAWATER_PLACE_20"] or 0),
            "land_area_part": int(raw["AREALAND_PART"] or 0),
            "water_area_part": int(raw["AREAWATER_PART"] or 0),
            "source": URL,
            "vintage": "2020 Census ZCTA-to-place relationship file",
            "retrieved_at": retrieved_at,
        })
    rows.sort(key=lambda row: (row["zcta"], row["place"]))
    out = ROOT / "data" / "normalized" / "zcta_place_relationships_2020.json"
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://www.census.gov/geographies/reference-files/2020/geo/relationship-files.html",
        "vintage": "2020 Census ZCTA-to-place relationship file",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "raw_rows": len(text.splitlines()) - 1,
    }
    manifest_path = ROOT / "data" / "raw" / "zcta_place_relationships_2020_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched {len(rows)} ZCTA-to-place relationships")


if __name__ == "__main__":
    main()
