#!/usr/bin/env python3
"""Fetch the first geography backbone from Census reference products."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

STATE_URL = "https://www2.census.gov/geo/docs/reference/state.txt"
COUNTY_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_counties_national.zip"
ZCTA_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2020_Gazetteer/2020_Gaz_zcta_national.zip"
ZCTA_COUNTY_REL_URL = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt"

CAPITALS = {
    "AL": "Montgomery", "AK": "Juneau", "AZ": "Phoenix", "AR": "Little Rock", "CA": "Sacramento",
    "CO": "Denver", "CT": "Hartford", "DE": "Dover", "DC": "Washington", "FL": "Tallahassee",
    "GA": "Atlanta", "HI": "Honolulu", "ID": "Boise", "IL": "Springfield", "IN": "Indianapolis",
    "IA": "Des Moines", "KS": "Topeka", "KY": "Frankfort", "LA": "Baton Rouge", "ME": "Augusta",
    "MD": "Annapolis", "MA": "Boston", "MI": "Lansing", "MN": "Saint Paul", "MS": "Jackson",
    "MO": "Jefferson City", "MT": "Helena", "NE": "Lincoln", "NV": "Carson City", "NH": "Concord",
    "NJ": "Trenton", "NM": "Santa Fe", "NY": "Albany", "NC": "Raleigh", "ND": "Bismarck",
    "OH": "Columbus", "OK": "Oklahoma City", "OR": "Salem", "PA": "Harrisburg", "RI": "Providence",
    "SC": "Columbia", "SD": "Pierre", "TN": "Nashville", "TX": "Austin", "UT": "Salt Lake City",
    "VT": "Montpelier", "VA": "Richmond", "WA": "Olympia", "WV": "Charleston", "WI": "Madison",
    "WY": "Cheyenne", "AS": "Pago Pago", "GU": "Hagåtña", "MP": "Saipan", "PR": "San Juan", "VI": "Charlotte Amalie"
}


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(req, timeout=60) as response:
        return response.read()


def main() -> None:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    state_raw = fetch(STATE_URL)
    (RAW / "census_state_reference.txt").write_bytes(state_raw)
    states = []
    for row in csv.DictReader(io.StringIO(state_raw.decode("utf-8")), delimiter="|"):
        states.append({
            "state_fips": row["STATE"],
            "abbr": row["STUSAB"],
            "name": row["STATE_NAME"],
            "statens": row["STATENS"],
            "capital": CAPITALS.get(row["STUSAB"]),
            "capital_source": "curated initial reference; validate against state government source"
        })
    (NORMALIZED / "states.json").write_text(json.dumps(states, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    county_zip = fetch(COUNTY_URL)
    (RAW / "census_counties_2023.zip").write_bytes(county_zip)
    with ZipFile(io.BytesIO(county_zip)) as archive:
        county_name = archive.namelist()[0]
        county_text = archive.read(county_name).decode("utf-8-sig")
    counties = [
        {key.strip(): value.strip() for key, value in row.items()}
        for row in csv.DictReader(io.StringIO(county_text), delimiter="\t")
    ]
    (NORMALIZED / "counties_2023.json").write_text(json.dumps(counties, indent=2) + "\n", encoding="utf-8")

    zcta_zip = fetch(ZCTA_URL)
    (RAW / "census_zcta_2020.zip").write_bytes(zcta_zip)
    with ZipFile(io.BytesIO(zcta_zip)) as archive:
        zcta_text = archive.read(archive.namelist()[0]).decode("utf-8-sig")
    zctas = [{key.strip(): value.strip() for key, value in row.items()} for row in csv.DictReader(io.StringIO(zcta_text), delimiter="\t")]
    (NORMALIZED / "zctas_2020.json").write_text(json.dumps(zctas, indent=2) + "\n", encoding="utf-8")

    rel_raw = fetch(ZCTA_COUNTY_REL_URL)
    (RAW / "zcta_county_relationship_2020.txt").write_bytes(rel_raw)
    relationships = [{key.strip(): value.strip() for key, value in row.items()} for row in csv.DictReader(io.StringIO(rel_raw.decode("utf-8-sig")), delimiter="|")]
    relationships = [
        {k: v for k, v in row.items() if k in {"GEOID_ZCTA5_20", "GEOID_COUNTY_20", "AREALAND_PART", "AREAWATER_PART"}}
        for row in relationships
        if row.get("GEOID_ZCTA5_20") and row.get("GEOID_COUNTY_20")
    ]
    (NORMALIZED / "zcta_county_relationships_2020.json").write_text(json.dumps(relationships, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "retrieved_at": retrieved_at,
        "files": [
            {"path": "data/raw/census_state_reference.txt", "source": STATE_URL, "records": len(states)},
            {"path": "data/normalized/states.json", "source": STATE_URL, "records": len(states)},
            {"path": "data/raw/census_counties_2023.zip", "source": COUNTY_URL, "records": len(counties)},
            {"path": "data/normalized/counties_2023.json", "source": COUNTY_URL, "records": len(counties)},
            {"path": "data/raw/census_zcta_2020.zip", "source": ZCTA_URL, "records": len(zctas)},
            {"path": "data/normalized/zctas_2020.json", "source": ZCTA_URL, "records": len(zctas)},
            {"path": "data/raw/zcta_county_relationship_2020.txt", "source": ZCTA_COUNTY_REL_URL, "records": len(relationships)},
            {"path": "data/normalized/zcta_county_relationships_2020.json", "source": ZCTA_COUNTY_REL_URL, "records": len(relationships)}
        ]
    }
    (RAW / "geography_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
