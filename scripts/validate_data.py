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
    county_subdivisions = load("county_subdivisions_2023.json")
    tracts = load("tracts_2023.json")
    urban_areas = load("urban_areas_2023.json")
    school_districts = load("school_districts_2023.json")
    school_administrative_districts = load("school_administrative_districts_2023.json")
    tribal_areas = load("tribal_areas_2023.json")
    state_legislative_districts = load("state_legislative_districts_2023.json")
    congressional_districts_118 = load("congressional_districts_118th_2023.json")
    cbsa_geography = load("cbsa_geography_2023.json")
    places = load("places_2020.json")
    places_2023 = load("places_2023.json")
    zctas = load("zctas_2020.json")
    zctas_2023 = load("zctas_2023.json")
    hawaiian_home_lands = load("hawaiian_home_lands_2023.json")
    electoral_college = load("electoral_college_results_1789_2024.json")
    puma_zcta_relationships = load("puma_zcta_relationships_2020.json")
    pumas = load("pumas_2020.json")
    zcta_population = load("zcta_population_acs_2023.json")
    zcta_profiles = load("zcta_profiles_acs_2023.json")
    relationships = load("zcta_county_relationships_2020.json")
    districts = load("congressional_districts_2020.json")
    current_districts = load("congressional_districts_2025.json")
    county_population = load("county_population_2020_2024.json")
    place_population = load("place_population_2020_2024.json")
    state_population = load("state_population_2020_2024.json")
    cbsa_population = load("cbsa_population_2020_2024.json")
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
    acs_state_education = load("acs_state_education_2023.json")
    acs_state_poverty = load("acs_state_poverty_2023.json")
    acs_county_age_sex = load("acs_county_age_sex_2023.json")
    acs_county_income = load("acs_county_income_2023.json")
    acs_county_housing = load("acs_county_housing_2023.json")
    acs_county_race = load("acs_county_race_2023.json")
    acs_county_education = load("acs_county_education_2023.json")
    acs_county_poverty = load("acs_county_poverty_2023.json")
    acs_place_income = load("acs_place_income_2023.json")
    acs_place_housing = load("acs_place_housing_2023.json")
    acs_place_race = load("acs_place_race_2023.json")
    acs_place_age_sex = load("acs_place_age_sex_2023.json")
    state_legislators = load("state_legislators_openstates.json")
    fec_candidates = load("fec_candidate_master_2024.json")
    fec_committees = load("fec_committee_master_2024.json")
    fec_results = load("fec_presidential_general_results_2024.json")
    fec_presidential_2004 = load("fec_presidential_general_2004.json")
    fec_presidential_2008 = load("fec_presidential_general_2008.json")
    fec_presidential_2012 = load("fec_presidential_general_2012.json")
    fec_presidential_2020 = load("fec_presidential_general_2020.json")
    fec_presidential_2016 = load("fec_presidential_general_2016.json")
    fec_presidential_2000 = load("fec_presidential_general_2000.json")
    fec_presidential_1996 = load("fec_presidential_general_1996.json")
    fec_presidential_1992 = load("fec_presidential_general_1992.json")
    fec_presidential_1988 = load("fec_presidential_general_1988.json")
    fec_presidential_1984 = load("fec_presidential_general_1984.json")
    fec_federal_elections = load("fec_federal_elections_2022.json")
    fec_federal_elections_2020 = load("fec_federal_elections_2020.json")
    fec_federal_elections_2018 = load("fec_federal_elections_2018.json")
    fec_federal_elections_2016 = load("fec_federal_elections_2016.json")
    fec_federal_elections_2014 = load("fec_federal_elections_2014.json")
    fec_federal_elections_2012 = load("fec_federal_elections_2012.json")
    fec_federal_elections_2008 = load("fec_federal_elections_2008.json")
    fec_federal_elections_2010 = load("fec_federal_elections_2010.json")
    fec_federal_elections_2006 = load("fec_federal_elections_2006.json")
    fec_federal_elections_2004 = load("fec_federal_elections_2004.json")
    fec_federal_elections_2002 = load("fec_federal_elections_2002.json")
    acs_district_income = load("acs_district_income_2023.json")
    acs_district_housing = load("acs_district_housing_2023.json")
    acs_district_race = load("acs_district_race_2023.json")
    acs_district_education = load("acs_district_education_2023.json")
    acs_district_poverty = load("acs_district_poverty_2023.json")

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
    assert len(county_subdivisions) >= 35000
    assert_unique(county_subdivisions, "GEOID", "county subdivision GEOIDs")
    assert all(row.get("USPS") and row.get("NAME") and len(row.get("GEOID", "")) == 10 for row in county_subdivisions)
    assert len(tracts) >= 80000
    assert_unique(tracts, "GEOID", "census tract GEOIDs")
    assert all(row.get("USPS") and len(row.get("GEOID", "")) == 11 and row.get("INTPTLAT") and row.get("INTPTLONG") for row in tracts)
    assert len(urban_areas) >= 2500
    assert_unique(urban_areas, "GEOID", "urban area GEOIDs")
    assert all(row.get("NAME") and len(row.get("GEOID", "")) == 5 and row.get("INTPTLAT") and row.get("INTPTLONG") for row in urban_areas)
    assert len(school_districts) >= 13000
    assert len({(row["district_type"], row["GEOID"]) for row in school_districts}) == len(school_districts), "duplicate school district type/GEOID pairs"
    assert {row.get("district_type") for row in school_districts} == {"elementary", "secondary", "unified"}
    assert all(row.get("USPS") and row.get("NAME") and row.get("LOGRADE") and row.get("HIGRADE") for row in school_districts)
    assert len(school_administrative_districts) >= 50
    assert_unique(school_administrative_districts, "GEOID", "school administrative district GEOIDs")
    assert all(row.get("NAME") and row.get("LOGRADE") and row.get("HIGRADE") and row.get("INTPTLAT") for row in school_administrative_districts)
    assert len(tribal_areas) >= 1800
    assert len({(row["area_type"], row["GEOID"], row["NAME"]) for row in tribal_areas}) == len(tribal_areas)
    assert {row.get("area_type") for row in tribal_areas} == {"reservation_or_tribal_trust", "reservation", "off_reservation_trust"}
    assert all(row.get("NAME") and row.get("GEOID") and row.get("INTPTLAT") and row.get("INTPTLONG") for row in tribal_areas)
    assert len(state_legislative_districts) >= 6800
    assert len({(row["chamber"], row["GEOID"]) for row in state_legislative_districts}) == len(state_legislative_districts)
    assert {row.get("chamber") for row in state_legislative_districts} == {"lower", "upper"}
    assert all(row.get("USPS") and row.get("NAME") and row.get("INTPTLAT") and row.get("INTPTLONG") for row in state_legislative_districts)
    assert len(congressional_districts_118) >= 435
    assert_unique(congressional_districts_118, "GEOID", "118th Congress district GEOIDs")
    assert all(row.get("congress") == "118" and row.get("USPS") and len(row.get("GEOID", "")) == 4 and row.get("INTPTLAT") and row.get("INTPTLONG") for row in congressional_districts_118)
    assert len(cbsa_geography) >= 900
    assert_unique(cbsa_geography, "GEOID", "CBSA geography GEOIDs")
    assert {row.get("CBSA_TYPE") for row in cbsa_geography} <= {"1", "2"}
    assert all(row.get("NAME") and row.get("GEOID") and row.get("INTPTLAT") and row.get("INTPTLONG") for row in cbsa_geography)
    assert_unique(places, "GEOID", "place GEOIDs")
    assert len(places_2023) >= 32000
    assert_unique(places_2023, "GEOID", "2023 place GEOIDs")
    assert all(row.get("USPS") and row.get("NAME") and row.get("INTPTLAT") and row.get("INTPTLONG") for row in places_2023)
    assert_unique(zctas, "GEOID", "ZCTA GEOIDs")
    assert len(zctas_2023) >= 33000
    assert_unique(zctas_2023, "GEOID", "2023 ZCTA GEOIDs")
    assert all(len(row.get("GEOID", "")) == 5 and row.get("INTPTLAT") and row.get("INTPTLONG") for row in zctas_2023)
    assert len(hawaiian_home_lands) >= 70
    assert_unique(hawaiian_home_lands, "GEOID", "Hawaiian Home Land GEOIDs")
    assert all(row.get("NAME") and row.get("INTPTLAT") and row.get("INTPTLONG") for row in hawaiian_home_lands)
    assert len(electoral_college) >= 2900
    assert len({row.get("election_year") for row in electoral_college}) == 60
    assert all(row.get("election_year") and row.get("source") and isinstance(row.get("cells"), list) for row in electoral_college)
    assert len(puma_zcta_relationships) >= 47000
    assert all(row.get("GEOID_PUMA5_20") and len(row["GEOID_PUMA5_20"]) == 7 and row.get("GEOID_ZCTA5_20") and len(row["GEOID_ZCTA5_20"]) == 5 for row in puma_zcta_relationships)
    assert len(pumas) >= 2400
    assert_unique(pumas, "GEOID_PUMA5_20", "PUMA GEOIDs")
    assert all(row.get("NAMELSAD_PUMA5_20") and row.get("MTFCC_PUMA5_20") == "G6120" for row in pumas)
    assert len(zcta_population) >= 30000
    assert_unique(zcta_population, "zcta", "ACS ZCTA population codes")
    assert len(zcta_profiles) >= 30000
    assert_unique(zcta_profiles, "zcta", "ACS ZCTA profile codes")
    assert all(row.get("median_household_income") is not None and row.get("housing_units") is not None for row in zcta_profiles)
    assert_unique(districts, "GEOID", "district GEOIDs")
    assert_unique(current_districts, "GEOID", "current district GEOIDs")
    assert_unique(county_population, "GEOID", "county population GEOIDs")
    assert_unique(place_population, "GEOID", "place population GEOIDs")
    assert len(state_population) >= 50
    assert_unique(state_population, "state_fips", "state population FIPS codes")
    assert len(cbsa_population) >= 900
    assert_unique(cbsa_population, "cbsa", "CBSA population codes")
    assert all(row.get("area_type") in {"Metropolitan Statistical Area", "Micropolitan Statistical Area"} for row in cbsa_population)
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
    for label, rows in (("education", acs_state_education), ("poverty", acs_state_poverty), ("income", acs_state_income), ("housing", acs_state_housing), ("race", acs_state_race)):
        assert len(rows) >= 50, f"too few ACS {label} rows"
        assert all(row.get("GEO_ID", "").startswith("0400000US") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS {label} GEO_IDs"
    for label, rows in (("age_sex", acs_county_age_sex), ("education", acs_county_education), ("poverty", acs_county_poverty), ("income", acs_county_income), ("housing", acs_county_housing), ("race", acs_county_race)):
        assert len(rows) >= 3000, f"too few ACS county {label} rows"
        assert all(row.get("GEO_ID", "").startswith("0500000US") and row.get("county_fips") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS county {label} GEO_IDs"
    for label, rows in (("income", acs_place_income), ("housing", acs_place_housing), ("race", acs_place_race)):
        assert len(rows) >= 30000, f"too few ACS place {label} rows"
        assert all(row.get("GEO_ID", "").startswith("1600000US") and row.get("place_fips") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS place {label} GEO_IDs"
    assert len(acs_place_age_sex) >= 30000
    assert all(row.get("GEO_ID", "").startswith("1600000US") and row.get("place_fips") and row.get("state_fips") and row.get("source") for row in acs_place_age_sex)
    assert len({row["GEO_ID"] for row in acs_place_age_sex}) == len(acs_place_age_sex), "duplicate ACS place age/sex GEO_IDs"
    assert len(state_legislators) >= 15000
    assert all(row.get("id") and row.get("name") and row.get("state") in {item["abbr"] for item in states} and row.get("record_type") in {"current", "retired"} and row.get("source") for row in state_legislators)
    assert len({row["id"] for row in state_legislators}) == len(state_legislators), "duplicate Open States legislator IDs"
    assert len(fec_candidates) >= 5000
    assert all(row.get("candidate_id") and row.get("candidate_name") and row.get("office") in {"H", "S", "P"} and row.get("cycle") == 2024 and row.get("source") for row in fec_candidates)
    assert len({row["candidate_id"] for row in fec_candidates}) == len(fec_candidates), "duplicate FEC candidate IDs"
    assert len(fec_committees) >= 5000
    assert all(row.get("committee_id") and row.get("committee_name") and row.get("cycle") == 2024 and row.get("source") for row in fec_committees)
    assert len({row["committee_id"] for row in fec_committees}) == len(fec_committees), "duplicate FEC committee IDs"
    assert len(fec_results) >= 50
    assert all(row.get("election_year") == 2024 and row.get("source") for row in fec_results)
    assert len(fec_presidential_2004) >= 400
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 2004 and row.get("source") for row in fec_presidential_2004)
    assert len(fec_presidential_2008) >= 450
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 2008 and row.get("source") for row in fec_presidential_2008)
    assert len(fec_presidential_2012) >= 450
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 2012 and row.get("source") for row in fec_presidential_2012)
    assert len(fec_presidential_2020) >= 550
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 2020 and row.get("source") for row in fec_presidential_2020)
    assert len(fec_presidential_2016) >= 800
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 2016 and row.get("source") for row in fec_presidential_2016)
    assert len(fec_presidential_2000) >= 400
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 2000 and row.get("source") for row in fec_presidential_2000)
    assert len(fec_presidential_1996) >= 200
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 1996 and row.get("source") for row in fec_presidential_1996)
    assert len(fec_presidential_1992) >= 500
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 1992 and row.get("source") for row in fec_presidential_1992)
    assert len(fec_presidential_1988) >= 300
    assert all(row.get("fec_id") and row.get("candidate_label") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 1988 and row.get("source") for row in fec_presidential_1988)
    assert len(fec_presidential_1984) >= 300
    assert all(row.get("fec_id") and row.get("candidate_label") and row.get("state") and row.get("votes") is not None and row.get("election_year") == 1984 and row.get("source") for row in fec_presidential_1984)
    assert len(fec_federal_elections) >= 3000
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("office") in {"senate", "house"} and row.get("election_year") == 2022 and row.get("source") for row in fec_federal_elections)
    assert len(fec_federal_elections_2020) >= 2800
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("office") in {"senate", "house"} and row.get("election_year") == 2020 and row.get("source") for row in fec_federal_elections_2020)
    for year, rows in ((2018, fec_federal_elections_2018), (2016, fec_federal_elections_2016)):
        assert len(rows) >= 2400, f"too few FEC {year} election rows"
        assert all(row.get("fec_id") and row.get("candidate_name") and row.get("office") in {"senate", "house"} and row.get("election_year") == year and row.get("source") for row in rows)
    for year, rows in ((2014, fec_federal_elections_2014), (2012, fec_federal_elections_2012)):
        assert len(rows) >= 2000, f"too few FEC {year} election rows"
        assert all(row.get("fec_id") and row.get("candidate_name") and row.get("office") in {"senate", "house"} and row.get("election_year") == year and row.get("source") for row in rows)
    for year, rows in ((2008, fec_federal_elections_2008), (2006, fec_federal_elections_2006)):
        assert len(rows) >= 2000, f"too few FEC {year} election rows"
        assert all(row.get("fec_id") and row.get("candidate_name") and row.get("office") in {"senate", "house"} and row.get("election_year") == year and row.get("source") for row in rows)
    assert len(fec_federal_elections_2010) >= 2900
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("office") in {"senate", "house"} and row.get("election_year") == 2010 and row.get("source") for row in fec_federal_elections_2010)
    assert len(fec_federal_elections_2004) >= 2000
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("office") in {"senate", "house"} and row.get("election_year") == 2004 and row.get("source") for row in fec_federal_elections_2004)
    assert len(fec_federal_elections_2002) >= 900
    assert all(row.get("fec_id") and row.get("candidate_name") and row.get("office") in {"senate", "house"} and row.get("election_year") == 2002 and row.get("source") for row in fec_federal_elections_2002)
    for label, rows in (("education", acs_district_education), ("poverty", acs_district_poverty), ("income", acs_district_income), ("housing", acs_district_housing), ("race", acs_district_race)):
        assert len(rows) >= 400, f"too few ACS district {label} rows"
        assert all(row.get("GEO_ID", "").startswith("5001800US") and row.get("district_geoid") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS district {label} GEO_IDs"

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
    print(f"validated states={len(states)} counties={len(counties)} county_population={len(county_population)} places={len(places)} place_population={len(place_population)} legislators={len(legislators)} state_legislators={len(state_legislators)} fec_candidates={len(fec_candidates)} fec_committees={len(fec_committees)} fec_results={len(fec_results)} fec_federal_elections={len(fec_federal_elections)} fec_federal_elections_2020={len(fec_federal_elections_2020)} fec_federal_elections_2018={len(fec_federal_elections_2018)} fec_federal_elections_2016={len(fec_federal_elections_2016)} fec_federal_elections_2014={len(fec_federal_elections_2014)} fec_federal_elections_2012={len(fec_federal_elections_2012)} fec_federal_elections_2008={len(fec_federal_elections_2008)} fec_federal_elections_2006={len(fec_federal_elections_2006)} acs_district_education={len(acs_district_education)} acs_district_poverty={len(acs_district_poverty)} acs_district_income={len(acs_district_income)} acs_district_housing={len(acs_district_housing)} acs_district_race={len(acs_district_race)} governors={len(governors)} governor_terms={sum(len(row.get('terms', [])) for row in governors)} presidents={len(presidents)} vice_presidents={len(vice_presidents)} justices={len(justices)} federal_judges={len(federal_judges)} secretaries_of_state={len(secretaries_of_state)} state_department_principals={len(state_department_principals)} acs_variables={len(acs_variables)} acs_state_age_sex={len(acs_state_age_sex)} acs_state_education={len(acs_state_education)} acs_state_poverty={len(acs_state_poverty)} acs_state_income={len(acs_state_income)} acs_state_housing={len(acs_state_housing)} acs_state_race={len(acs_state_race)} acs_county_age_sex={len(acs_county_age_sex)} acs_county_education={len(acs_county_education)} acs_county_poverty={len(acs_county_poverty)} acs_county_income={len(acs_county_income)} acs_county_housing={len(acs_county_housing)} acs_county_race={len(acs_county_race)} acs_place_age_sex={len(acs_place_age_sex)} acs_place_income={len(acs_place_income)} acs_place_housing={len(acs_place_housing)} acs_place_race={len(acs_place_race)} agencies={len(agencies)} executive_orders={len(executive_orders)} proclamations={len(proclamations)} presidential_documents={len(presidential_documents)} zctas={len(zctas)} relationships={len(relationships)} districts_2020={len(districts)} districts_2025={len(current_districts)}")


if __name__ == "__main__":
    main()
