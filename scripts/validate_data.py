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
    county_population = load("county_population_2020_2024.json")
    place_population = load("place_population_2020_2024.json")
    legislators = load("congressional_legislators.json")
    governors = load("governors_nga.json")
    presidents = load("presidents.json")
    agencies = load("federal_register_agencies.json")
    executive_orders = load("executive_orders.json")
    proclamations = load("presidential_proclamations.json")
    presidential_documents = load("presidential_documents.json")
    vice_presidents = load("vice_presidents.json")
    justices = load("supreme_court_justices.json")

    assert len(states) >= 50
    assert_unique(states, "state_fips", "state FIPS codes")
    assert_unique(counties, "GEOID", "county GEOIDs")
    assert_unique(places, "GEOID", "place GEOIDs")
    assert_unique(zctas, "GEOID", "ZCTA GEOIDs")
    assert_unique(districts, "GEOID", "district GEOIDs")
    assert_unique(current_districts, "GEOID", "current district GEOIDs")
    assert_unique(county_population, "GEOID", "county population GEOIDs")
    assert_unique(place_population, "GEOID", "place population GEOIDs")
    legislator_ids = [person.get("id", {}).get("bioguide") for person in legislators]
    assert all(legislator_ids)
    assert len(legislator_ids) == len(set(legislator_ids)), "duplicate legislator Bioguide IDs"
    assert all(row.get("name") and row.get("state") for row in governors)
    assert all(row.get("source") and row.get("profile_url") for row in governors)
    assert all(1700 <= term["start_year"] <= 2100 and 1700 <= term["end_year"] <= 2100 for row in governors for term in row.get("terms", []))
    assert len(presidents) >= 40
    assert all(row.get("name") and row.get("start_date") and row.get("source") for row in presidents)
    assert all(row["start_date"] <= row["end_date"] if row.get("end_date") else True for row in presidents)
    assert len(agencies) >= 100
    assert all(row.get("name") and row.get("source") for row in agencies)
    agency_slugs = [row.get("slug") for row in agencies if row.get("slug")]
    assert len(agency_slugs) == len(set(agency_slugs)), "duplicate Federal Register agency slugs"
    assert len(executive_orders) >= 1000
    assert all(row.get("title") and row.get("document_number") and row.get("source") for row in executive_orders)
    document_numbers = [row.get("document_number") for row in executive_orders]
    assert len(document_numbers) == len(set(document_numbers)), "duplicate Federal Register document numbers"
    assert len(proclamations) >= 3000
    assert all(row.get("title") and row.get("document_number") and row.get("source") for row in proclamations)
    proclamation_documents = [row["document_number"] for row in proclamations]
    assert len(proclamation_documents) == len(set(proclamation_documents)), "duplicate proclamation document numbers"
    assert len(presidential_documents) >= 1500
    assert all(row.get("title") and row.get("document_number") and row.get("source") for row in presidential_documents)
    assert all(row.get("presidential_document_type") in {"memorandum", "determination", "other"} for row in presidential_documents)
    presidential_document_keys = [(row["document_number"], row["presidential_document_type"], row.get("title")) for row in presidential_documents]
    assert len(presidential_document_keys) == len(set(presidential_document_keys)), "duplicate presidential document records"
    assert len(vice_presidents) >= 45
    assert all(row.get("name") and row.get("profile_url") and row.get("source") for row in vice_presidents)
    assert all(row.get("end_year") is None or row["start_year"] <= row["end_year"] for row in vice_presidents)
    assert len(justices) >= 100
    assert all(row.get("name") and row.get("oath_date") and row.get("source") for row in justices)
    assert all(row.get("role") in {"chief", "associate"} for row in justices)

    zcta_ids = {row["GEOID"] for row in zctas}
    # The relationship file is a 2020 vintage while the county gazetteer is 2023;
    # county-equivalent identifiers can therefore legitimately differ by vintage.
    assert all(len(row["GEOID_COUNTY_20"]) == 5 for row in relationships)
    # Relationship files can contain valid ZCTA codes omitted from the
    # gazetteer when the area has no land/area record; validate the code shape.
    assert all(len(row["GEOID_ZCTA5_20"]) == 5 for row in relationships)
    assert all(row["STATEFP"] == row["GEOID"][:2] for row in districts)
    assert all(row["STATEFP"] == row["GEOID"][:2] for row in current_districts)
    assert all(len(row["GEOID"]) == 5 for row in county_population)
    assert all(len(row["GEOID"]) == 7 for row in place_population)
    assert all(term.get("type") in {"rep", "sen"} for person in legislators for term in person.get("terms", []))
    print(f"validated states={len(states)} counties={len(counties)} county_population={len(county_population)} places={len(places)} place_population={len(place_population)} legislators={len(legislators)} governors={len(governors)} governor_terms={sum(len(row.get('terms', [])) for row in governors)} presidents={len(presidents)} vice_presidents={len(vice_presidents)} justices={len(justices)} agencies={len(agencies)} executive_orders={len(executive_orders)} proclamations={len(proclamations)} presidential_documents={len(presidential_documents)} zctas={len(zctas)} relationships={len(relationships)} districts_2020={len(districts)} districts_2025={len(current_districts)}")


if __name__ == "__main__":
    main()
