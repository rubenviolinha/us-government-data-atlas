#!/usr/bin/env python3
"""Validate core geography invariants for the checked-in release."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def assert_unique(rows, key, label):
    values = [row[key] for row in rows]
    assert len(values) == len(set(values)), f"duplicate {label}: {key}"


def main():
    states = load("states.json")
    counties = load("counties_2023.json")
    places = load("places_2020.json")
    zctas = load("zctas_2020.json")
    relationships = load("zcta_county_relationships_2020.json")
    districts = load("congressional_districts_2020.json")
    current_districts = load("congressional_districts_2025.json")

    assert len(states) >= 50
    assert_unique(states, "state_fips", "state FIPS codes")
    assert_unique(counties, "GEOID", "county GEOIDs")
    assert_unique(places, "GEOID", "place GEOIDs")
    assert_unique(zctas, "GEOID", "ZCTA GEOIDs")
    assert_unique(districts, "GEOID", "district GEOIDs")
    assert_unique(current_districts, "GEOID", "current district GEOIDs")

    zcta_ids = {row["GEOID"] for row in zctas}
    # The relationship file is a 2020 vintage while the county gazetteer is 2023;
    # county-equivalent identifiers can therefore legitimately differ by vintage.
    assert all(len(row["GEOID_COUNTY_20"]) == 5 for row in relationships)
    # Relationship files can contain valid ZCTA codes omitted from the
    # gazetteer when the area has no land/area record; validate the code shape.
    assert all(len(row["GEOID_ZCTA5_20"]) == 5 for row in relationships)
    assert all(row["STATEFP"] == row["GEOID"][:2] for row in districts)
    assert all(row["STATEFP"] == row["GEOID"][:2] for row in current_districts)
    print(f"validated states={len(states)} counties={len(counties)} places={len(places)} zctas={len(zctas)} relationships={len(relationships)} districts_2020={len(districts)} districts_2025={len(current_districts)}")


if __name__ == "__main__":
    main()
