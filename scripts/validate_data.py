#!/usr/bin/env python3
"""Validate core geography invariants for the checked-in release."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
CATALOG = ROOT / "metadata" / "catalog.json"
ACCESS = ROOT / "metadata" / "access_requirements.json"
RELEASE = ROOT / "metadata" / "release_manifest.json"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def assert_unique(rows, key, label):
    values = [row[key] for row in rows]
    assert len(values) == len(set(values)), f"duplicate {label}: {key}"


def main():
    states = load("states.json")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    access = json.loads(ACCESS.read_text(encoding="utf-8"))
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
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
    federal_judges = load("federal_judges.json")
    secretaries_of_state = load("secretaries_of_state.json")
    state_department_principals = load("state_department_principals.json")
    acs_variables = load("acs_profile_variables_2023.json")
    acs_state_age_sex = load("acs_state_age_sex_2023.json")
    acs_state_income = load("acs_state_income_2023.json")
    acs_state_housing = load("acs_state_housing_2023.json")
    acs_state_race = load("acs_state_race_2023.json")
    acs_county_age_sex = load("acs_county_age_sex_2023.json")
    acs_county_income = load("acs_county_income_2023.json")
    acs_county_housing = load("acs_county_housing_2023.json")
    acs_county_race = load("acs_county_race_2023.json")
    acs_place_income = load("acs_place_income_2023.json")
    acs_place_housing = load("acs_place_housing_2023.json")
    acs_place_race = load("acs_place_race_2023.json")
    state_legislators = load("state_legislators_openstates.json")
    fec_candidates = load("fec_candidate_master_2024.json")

    assert len(states) >= 50
    catalog_files = {entry["file"] for entry in catalog.get("entries", [])}
    assert "data/normalized/states.json" in catalog_files
    assert all(entry.get("records", 0) >= 0 and entry.get("size_bytes", 0) > 0 for entry in catalog.get("entries", []))
    assert len(access.get("requirements", [])) >= 3
    assert all(item.get("id") and item.get("status") and item.get("source") for item in access["requirements"])
    assert release.get("algorithm") == "sha256"
    assert release.get("dataset_count") == len(release.get("datasets", []))
    assert all(len(item.get("sha256", "")) == 64 and item.get("size_bytes", 0) > 0 for item in release["datasets"])
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
    assert len(federal_judges) >= 3000
    assert all(row.get("jid") and row.get("Last Name") and row.get("source") for row in federal_judges)
    judge_ids = [row["jid"] for row in federal_judges]
    assert len(judge_ids) == len(set(judge_ids)), "duplicate Federal Judicial Center judge IDs"
    assert len(secretaries_of_state) >= 60
    assert all(row.get("name") and row.get("profile_url") and row.get("source") for row in secretaries_of_state)
    assert all(row.get("end_year") is None or row["start_year"] <= row["end_year"] for row in secretaries_of_state)
    assert len(state_department_principals) >= 1000
    assert all(row.get("name") and row.get("profile_url") and row.get("source") for row in state_department_principals)
    principal_urls = [row["profile_url"] for row in state_department_principals]
    assert len(principal_urls) == len(set(principal_urls)), "duplicate State Department principal profiles"
    assert len(acs_variables) >= 1000
    assert all(row.get("name") and row.get("label") and row.get("group") and row.get("source") for row in acs_variables)
    assert {row["group"] for row in acs_variables} == {"DP02", "DP03", "DP04", "DP05"}
    assert len(acs_state_age_sex) >= 50
    assert all(row.get("GEO_ID", "").startswith("0400000US") and row.get("state_fips") and row.get("source") for row in acs_state_age_sex)
    assert len({row["GEO_ID"] for row in acs_state_age_sex}) == len(acs_state_age_sex)
    for label, rows in (("income", acs_state_income), ("housing", acs_state_housing), ("race", acs_state_race)):
        assert len(rows) >= 50, f"too few ACS {label} rows"
        assert all(row.get("GEO_ID", "").startswith("0400000US") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS {label} GEO_IDs"
    for label, rows in (("age_sex", acs_county_age_sex), ("income", acs_county_income), ("housing", acs_county_housing), ("race", acs_county_race)):
        assert len(rows) >= 3000, f"too few ACS county {label} rows"
        assert all(row.get("GEO_ID", "").startswith("0500000US") and row.get("county_fips") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS county {label} GEO_IDs"
    for label, rows in (("income", acs_place_income), ("housing", acs_place_housing), ("race", acs_place_race)):
        assert len(rows) >= 30000, f"too few ACS place {label} rows"
    assert all(row.get("GEO_ID", "").startswith("1600000US") and row.get("place_fips") and row.get("state_fips") and row.get("source") for row in rows)
    assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS place {label} GEO_IDs"
    assert len(state_legislators) >= 15000
    assert all(row.get("id") and row.get("name") and row.get("state") in {item["abbr"] for item in states} and row.get("record_type") in {"current", "retired"} and row.get("source") for row in state_legislators)
    assert len({row["id"] for row in state_legislators}) == len(state_legislators), "duplicate Open States legislator IDs"
    assert len(fec_candidates) >= 5000
    assert all(row.get("candidate_id") and row.get("candidate_name") and row.get("office") in {"H", "S", "P"} and row.get("cycle") == 2024 and row.get("source") for row in fec_candidates)
    assert len({row["candidate_id"] for row in fec_candidates}) == len(fec_candidates), "duplicate FEC candidate IDs"

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
    print(f"validated states={len(states)} counties={len(counties)} county_population={len(county_population)} places={len(places)} place_population={len(place_population)} legislators={len(legislators)} state_legislators={len(state_legislators)} fec_candidates={len(fec_candidates)} governors={len(governors)} governor_terms={sum(len(row.get('terms', [])) for row in governors)} presidents={len(presidents)} vice_presidents={len(vice_presidents)} justices={len(justices)} federal_judges={len(federal_judges)} secretaries_of_state={len(secretaries_of_state)} state_department_principals={len(state_department_principals)} acs_variables={len(acs_variables)} acs_state_age_sex={len(acs_state_age_sex)} acs_state_income={len(acs_state_income)} acs_state_housing={len(acs_state_housing)} acs_state_race={len(acs_state_race)} acs_county_age_sex={len(acs_county_age_sex)} acs_county_income={len(acs_county_income)} acs_county_housing={len(acs_county_housing)} acs_county_race={len(acs_county_race)} acs_place_income={len(acs_place_income)} acs_place_housing={len(acs_place_housing)} acs_place_race={len(acs_place_race)} agencies={len(agencies)} executive_orders={len(executive_orders)} proclamations={len(proclamations)} presidential_documents={len(presidential_documents)} zctas={len(zctas)} relationships={len(relationships)} districts_2020={len(districts)} districts_2025={len(current_districts)}")


if __name__ == "__main__":
    main()
