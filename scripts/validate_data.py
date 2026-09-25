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
    zbp_totals = load("zbp_totals_2022.json")
    zbp_totals_2023 = load("zbp_totals_2023.json")
    cbp_county_totals = load("cbp_county_totals_2023.json")
    cbp_cbsa_totals = load("cbp_cbsa_totals_2023.json")
    cbp_csa_totals = load("cbp_csa_totals_2023.json")
    zctas_2023 = load("zctas_2023.json")
    hawaiian_home_lands = load("hawaiian_home_lands_2023.json")
    electoral_college = load("electoral_college_results_1789_2024.json")
    puma_zcta_relationships = load("puma_zcta_relationships_2020.json")
    pumas = load("pumas_2020.json")
    puma_cousub_relationships = load("puma_cousub_relationships_2020.json")
    puma_vintage_relationships = load("puma_vintage_relationships_2020_2010.json")
    place_vintage_relationships = load("place_vintage_relationships_2020_2010.json")
    cbsa_vintage_relationships = load("cbsa_vintage_relationships_2020_2023.json")
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
    senators = load("senators.json")
    representatives = load("representatives.json")
    current_senators = load("current_senators.json")
    current_representatives = load("current_representatives.json")
    governors = load("governors_nga.json")
    current_governors = load("current_governors_nga.json")
    presidents = load("presidents.json")
    agencies = load("federal_register_agencies.json")
    agency_relationships = load("federal_agency_relationships.json")
    executive_orders = load("executive_orders.json")
    proclamations = load("presidential_proclamations.json")
    presidential_documents = load("presidential_documents.json")
    vice_presidents = load("vice_presidents.json")
    justices = load("supreme_court_justices.json")
    current_justices = load("current_supreme_court_justices.json")
    federal_judges = load("federal_judges.json")
    current_federal_judges = load("current_federal_judges.json")
    federal_court_index = load("federal_court_index.json")
    state_summary = load("state_summary.json")
    svi_counties = load("svi_counties_2022.json")
    svi_tracts = []
    for path in sorted((ROOT / "data" / "normalized").glob("svi_tracts_2022_part*.json")):
        svi_tracts.extend(json.loads(path.read_text(encoding="utf-8")))
    svi_zctas = load("svi_zctas_2022.json")
    zcta_acs_2024 = load("zcta_profiles_acs_2024.json")
    zcta_population_acs_2024 = load("zcta_population_acs_2024.json")
    acs_cousub_2024 = {label: load(f"acs_cousub_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_school_2024 = {label: load(f"acs_school_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_school_elementary_2024 = {label: load(f"acs_school_elementary_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_school_secondary_2024 = {label: load(f"acs_school_secondary_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_consolidated_city_2024 = {label: load(f"acs_consolidated_city_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_anrc_2024 = {label: load(f"acs_alaska_native_regional_corporation_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_principal_city_2024 = {label: load(f"acs_principal_city_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_metropolitan_division_2024 = {label: load(f"acs_metropolitan_division_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_other_special_2024 = {
        geo_type: {label: load(f"acs_{geo_type}_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
        for geo_type in ("subminor_civil_division", "tribal_subdivision_or_remainder", "american_indian_area_reservation_statistical", "off_reservation_trust_land_hawaiian_homeland", "tribal_census_tract", "tribal_block_group")
    }
    acs_tract_2024 = {label: load(f"acs_tract_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_urban_2024 = {label: load(f"acs_urban_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_district_2024_5yr = {label: load(f"acs_district_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_aiannh_2024 = {label: load(f"acs_aiannh_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_state_legislative_2024 = {(chamber, label): load(f"acs_state_legislative_{chamber}_{label}_2024_5yr.json") for chamber in ("upper", "lower") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_cbsa_2024_5yr = {label: load(f"acs_cbsa_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    acs_csa_2024_5yr = {label: load(f"acs_csa_{label}_2024_5yr.json") for label in ("age_sex", "education", "poverty", "income", "housing", "race")}
    current_cabinet = load("current_cabinet_white_house.json")
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
    acs_place_education = load("acs_place_education_2023.json")
    acs_place_poverty = load("acs_place_poverty_2023.json")
    state_legislators = load("state_legislators_openstates.json")
    state_legislators_upper = load("state_legislators_upper.json")
    state_legislators_lower = load("state_legislators_lower.json")
    current_state_legislators_upper = load("current_state_legislators_upper.json")
    current_state_legislators_lower = load("current_state_legislators_lower.json")
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
    acs_district_age_sex = load("acs_district_age_sex_2023.json")
    acs_puma_age_sex = load("acs_puma_age_sex_2023.json")
    acs_puma_education = load("acs_puma_education_2023.json")
    acs_puma_poverty = load("acs_puma_poverty_2023.json")
    acs_puma_income = load("acs_puma_income_2023.json")
    acs_puma_housing = load("acs_puma_housing_2023.json")
    acs_puma_race = load("acs_puma_race_2023.json")
    noaa_state_climate = load("noaa_state_climate_1895_2024.json")
    acs_school_age_sex = load("acs_school_age_sex_2023.json")
    acs_school_education = load("acs_school_education_2023.json")
    acs_school_poverty = load("acs_school_poverty_2023.json")
    acs_school_income = load("acs_school_income_2023.json")
    acs_school_housing = load("acs_school_housing_2023.json")
    acs_school_race = load("acs_school_race_2023.json")
    acs_cousub_age_sex = load("acs_cousub_age_sex_2023.json")
    acs_cousub_income = load("acs_cousub_income_2023.json")
    acs_cousub_poverty = load("acs_cousub_poverty_2023.json")
    acs_cousub_education = load("acs_cousub_education_2023.json")
    acs_cousub_housing = load("acs_cousub_housing_2023.json")
    acs_cousub_race = load("acs_cousub_race_2023.json")

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
    assert len(zbp_totals) >= 30000
    assert len({row.get("zip_code") for row in zbp_totals}) == len(zbp_totals)
    assert all(len(row.get("zip_code", "")) == 5 and row.get("source") and row.get("vintage") == "2022 ZBP totals" for row in zbp_totals)
    assert len(zbp_totals_2023) >= 30000
    assert len({row.get("zip_code") for row in zbp_totals_2023}) == len(zbp_totals_2023)
    assert all(len(row.get("zip_code", "")) == 5 and row.get("source") and row.get("vintage") == "2023 ZBP totals" for row in zbp_totals_2023)
    assert len(cbp_county_totals) >= 3000
    assert_unique(cbp_county_totals, "GEOID", "CBP county total GEOIDs")
    assert all(len(row.get("GEOID", "")) == 5 and row.get("naics") == "00" and row.get("source") for row in cbp_county_totals)
    assert len(cbp_cbsa_totals) >= 900
    assert_unique(cbp_cbsa_totals, "cbsa", "CBP CBSA total codes")
    assert all(len(row.get("cbsa", "")) == 5 and row.get("naics") == "00" and row.get("source") for row in cbp_cbsa_totals)
    assert len(cbp_csa_totals) >= 100
    assert_unique(cbp_csa_totals, "csa", "CBP CSA total codes")
    assert all(row.get("csa") and row.get("naics") == "00" and row.get("source") for row in cbp_csa_totals)
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
    assert len(puma_cousub_relationships) >= 38000
    assert all(row.get("GEOID_PUMA5_20") and len(row["GEOID_PUMA5_20"]) == 7 and row.get("GEOID_COUSUB_20") and len(row["GEOID_COUSUB_20"]) == 10 for row in puma_cousub_relationships)
    assert len(puma_vintage_relationships) >= 6800
    assert all(row.get("GEOID_PUMA5_20") and len(row["GEOID_PUMA5_20"]) == 7 and row.get("GEOID_PUMA5_10") and len(row["GEOID_PUMA5_10"]) == 7 for row in puma_vintage_relationships)
    assert len(place_vintage_relationships) >= 38000
    assert all(row.get("GEOID_PLACE_20") and len(row["GEOID_PLACE_20"]) == 7 and row.get("GEOID_PLACE_10") and len(row["GEOID_PLACE_10"]) == 7 for row in place_vintage_relationships)
    assert len(cbsa_vintage_relationships) >= 900
    assert all(row.get("GEOID_CBSA_20") and len(row["GEOID_CBSA_20"]) == 5 and row.get("GEOID_CBSA_23") and len(row["GEOID_CBSA_23"]) == 5 for row in cbsa_vintage_relationships)
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
    for label, rows, office_type in (("senator", senators, "sen"), ("representative", representatives, "rep")):
        ids = [person.get("id", {}).get("bioguide") for person in rows]
        assert ids and len(ids) == len(set(ids)), f"duplicate {label} Bioguide IDs"
        assert all(person.get("office_scope") == label and person.get("source") and any(term.get("type") == office_type for term in person.get("terms", [])) for person in rows)
    assert len(current_senators) >= 90 and len(current_representatives) >= 400
    assert all(person.get("view_as_of") and person.get("office_scope") in {"senator", "representative"} for person in current_senators + current_representatives)
    assert len(current_state_legislators_upper) >= 1500 and len(current_state_legislators_lower) >= 4000
    assert all(row.get("view_as_of") and row.get("chamber_scope") in {"upper", "lower"} for row in current_state_legislators_upper + current_state_legislators_lower)
    assert all(row.get("name") and row.get("state") for row in governors)
    for chamber, rows in (("upper", state_legislators_upper), ("lower", state_legislators_lower)):
        ids = [row.get("id") for row in rows]
        assert ids and len(ids) == len(set(ids)), f"duplicate state {chamber} legislator IDs"
        assert all(row.get("chamber_scope") == chamber and any(role.get("type") == chamber for role in row.get("roles", [])) for row in rows)
    assert all(row.get("source") and row.get("profile_url") for row in governors)
    assert len(current_governors) >= 50
    assert len({row.get("state") for row in current_governors}) == len(current_governors)
    assert all(row.get("name") and row.get("profile_url") and row.get("source") and row.get("retrieved_at") for row in current_governors)
    assert all(1700 <= term["start_year"] <= 2100 and 1700 <= term["end_year"] <= 2100 for row in governors for term in row.get("terms", []))
    assert len(presidents) >= 40
    assert all(row.get("name") and row.get("start_date") and row.get("source") for row in presidents)
    assert all(row["start_date"] <= row["end_date"] if row.get("end_date") else True for row in presidents)
    assert len(agencies) >= 100
    assert all(row.get("name") and row.get("source") for row in agencies)
    agency_slugs = [row.get("slug") for row in agencies if row.get("slug")]
    assert len(agency_slugs) == len(set(agency_slugs)), "duplicate Federal Register agency slugs"
    agency_ids = {row["id"] for row in agencies}
    assert agency_relationships
    assert all(row.get("parent_id") in agency_ids and row.get("child_id") in agency_ids and row.get("relationship") == "parent_child" and row.get("source") for row in agency_relationships)
    assert len({(row["parent_id"], row["child_id"]) for row in agency_relationships}) == len(agency_relationships)
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
    assert len(current_justices) >= 9
    assert all(row.get("view_as_of") and row.get("view_type") == "currently_serving" for row in current_justices)
    assert all(not row.get("service_terminated_date") or row["service_terminated_date"] >= row["view_as_of"] for row in current_justices)
    assert len(federal_judges) >= 3000
    assert all(row.get("jid") and row.get("Last Name") and row.get("source") for row in federal_judges)
    judge_ids = [row["jid"] for row in federal_judges]
    assert len(judge_ids) == len(set(judge_ids)), "duplicate Federal Judicial Center judge IDs"
    assert len(current_federal_judges) >= 500
    assert all(row.get("jid") and row.get("view_as_of") and row.get("view_type") == "currently_serving" and row.get("active_appointments") for row in current_federal_judges)
    assert all(all(appointment.get("commission_date") and (not appointment.get("termination_date") or appointment["termination_date"] >= row["view_as_of"]) for appointment in row["active_appointments"]) for row in current_federal_judges)
    assert len(federal_court_index) >= 150
    assert len({row.get("court_name") for row in federal_court_index}) == len(federal_court_index)
    assert all(row.get("court_name") and row.get("court_type") and row.get("historical_judge_records", 0) > 0 and row.get("source") for row in federal_court_index)
    assert len(state_summary) == 57
    assert len({row.get("state_fips") for row in state_summary}) == 57
    assert all(row.get("state_name") and row.get("source") for row in state_summary)
    assert sum(bool(row.get("population_2025")) for row in state_summary) >= 52
    assert len(svi_counties) >= 3000
    assert len({row.get("GEOID") for row in svi_counties}) == len(svi_counties)
    assert all(len(row.get("GEOID", "")) == 5 and row.get("RPL_THEMES") is not None and row.get("source") for row in svi_counties)
    assert len(svi_tracts) >= 84000
    assert len({row.get("GEOID") for row in svi_tracts}) == len(svi_tracts)
    assert all(len(row.get("GEOID", "")) == 11 and row.get("RPL_THEMES") is not None and row.get("source") for row in svi_tracts)
    assert len(svi_zctas) >= 33000
    assert len({row.get("GEOID") for row in svi_zctas}) == len(svi_zctas)
    assert all(len(row.get("GEOID", "")) == 5 and row.get("Overall_SVI_Percentile") is not None and row.get("comparison") == "national" and row.get("source") for row in svi_zctas)
    assert len(zcta_acs_2024) >= 33000 and len({row.get("zcta") for row in zcta_acs_2024}) == len(zcta_acs_2024)
    assert all(row.get("source_vintage") == "ACS 2024 5-year" for row in zcta_acs_2024)
    assert len(zcta_population_acs_2024) == len(zcta_acs_2024) and all(row.get("population") is not None and row.get("source") for row in zcta_population_acs_2024)
    assert len(current_cabinet) >= 15
    assert len({row.get("title") for row in current_cabinet}) == len(current_cabinet)
    assert all(row.get("name") and row.get("title") and row.get("source") and row.get("retrieved_at") for row in current_cabinet)
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
    for puma_rows in (acs_puma_age_sex, acs_puma_education, acs_puma_poverty, acs_puma_income, acs_puma_housing, acs_puma_race):
        assert len(puma_rows) >= 2400
        assert len({row.get("puma_geoid") for row in puma_rows}) == len(puma_rows)
        assert all(row.get("puma_geoid") and len(row["puma_geoid"]) == 7 and row.get("source") and row.get("vintage") == "2023 ACS 1-year" for row in puma_rows)

    acs_puma_5yr = [load(name) for name in (
        "acs_puma_age_sex_2023_5yr.json",
        "acs_puma_education_2023_5yr.json",
        "acs_puma_poverty_2023_5yr.json",
        "acs_puma_income_2023_5yr.json",
        "acs_puma_housing_2023_5yr.json",
        "acs_puma_race_2023_5yr.json",
    )]
    for puma_rows in acs_puma_5yr:
        assert len(puma_rows) >= 2400
        assert len({row.get("puma_geoid") for row in puma_rows}) == len(puma_rows)
        assert all(row.get("puma_geoid") and len(row["puma_geoid"]) == 7 and row.get("source") and row.get("vintage") == "2023 ACS 5-year" for row in puma_rows)

    counties_2024 = load("counties_2024.json")
    zctas_2024 = load("zctas_2024.json")
    cbsa_2024 = load("cbsa_geography_2024.json")
    places_2024 = load("places_2024.json")
    tracts_2024 = load("tracts_2024.json")
    ballot_candidates_2024 = load("fec_congressional_ballot_candidates_2024.json")
    election_directory_2025 = load("fec_state_election_directory_2025.json")
    presidential_ballots_2024 = load("fec_presidential_ballot_candidates_2024.json")
    gazetteer_2025 = {
        "congressional_districts_119th_2025.json": 440,
        "american_indian_alaska_native_areas_2025.json": 704,
        "american_indian_alaska_native_reservations_2025.json": 867,
        "cbsa_geography_2025.json": 935,
        "counties_2025.json": 3222,
        "county_subdivisions_2025.json": 36427,
        "elementary_school_districts_2025.json": 1971,
        "places_2025.json": 32350,
        "secondary_school_districts_2025.json": 478,
        "school_administrative_districts_2025.json": 52,
        "state_legislative_districts_lower_2025.json": 4879,
        "state_legislative_districts_upper_2025.json": 1964,
        "states_2025.json": 52,
        "tracts_2025.json": 85396,
        "urban_areas_2025.json": 2644,
        "unified_school_districts_2025.json": 10863,
        "zctas_2025.json": 33791,
    }
    assert len(counties_2024) == 3222
    assert len(zctas_2024) == 33791
    assert len(cbsa_2024) == 935
    assert len(places_2024) == 32333
    assert len(tracts_2024) == 85396
    assert len(ballot_candidates_2024) >= 1100
    assert all(row.get("fec_id_number") and row.get("candidate_name") and row.get("office") in {"house", "senate"} for row in ballot_candidates_2024)
    assert len(election_directory_2025) >= 55
    assert len({row["state_fips"] for row in election_directory_2025}) == len(election_directory_2025)
    assert all(row.get("state_name") and row.get("source") for row in election_directory_2025)
    assert sum(bool(row.get("section_available")) for row in election_directory_2025) >= 55
    assert len(presidential_ballots_2024) >= 300
    assert len({(row["state_abbreviation"], row["candidate_label"]) for row in presidential_ballots_2024}) == len(presidential_ballots_2024)
    assert all(row.get("source") and row.get("candidate_label") for row in presidential_ballots_2024)
    for filename, expected in gazetteer_2025.items():
        rows = load(filename)
        assert len(rows) == expected, (filename, len(rows), expected)
        assert len({row.get("GEOID") for row in rows}) == len(rows), filename
    population_2025 = {
        "state_population_2020_2025.json": 52,
        "county_population_2020_2025.json": 3144,
        "place_population_2020_2025.json": 19483,
        "cbsa_population_2020_2025.json": 925,
        "csa_population_2020_2025.json": 181,
    }
    for filename, expected in population_2025.items():
        rows = load(filename)
        assert len(rows) == expected, (filename, len(rows), expected)
        assert all(row.get("source_vintage") == "2020-2025" and row.get("population_2025") for row in rows), filename
    minimum = {"county": 800, "place": 500}
    for geo_kind, expected in (("state", 52), ("district", 437), ("county", None), ("place", None), ("puma", None)):
        geoid_key = {"state": "state_geoid", "district": "district_geoid", "county": "county_geoid", "place": "place_geoid", "puma": "puma_geoid"}[geo_kind]
        for label in ("age_sex", "education", "poverty", "income", "housing", "race"):
            rows = load(f"acs_{geo_kind}_{label}_2024.json")
            if expected is not None:
                assert len(rows) == expected, (geo_kind, label, len(rows), expected)
            elif geo_kind in minimum:
                assert len(rows) >= minimum[geo_kind], (geo_kind, label, len(rows))
            else:
                assert len(rows) >= 2300, (geo_kind, label, len(rows))
            assert len({row[geoid_key] for row in rows}) == len(rows)
            assert all(row.get("source") and row.get("vintage") == "2024 ACS 1-year" for row in rows)
    for geo_kind, expected in (("county", 3222), ("place", 32330)):
        geoid_key = {"county": "county_geoid", "place": "place_geoid"}[geo_kind]
        for label in ("age_sex", "education", "poverty", "income", "housing", "race"):
            rows = load(f"acs_{geo_kind}_{label}_2024_5yr.json")
            assert len(rows) == expected, (geo_kind, label, len(rows), expected)
            assert len({row[geoid_key] for row in rows}) == len(rows)
            assert all(row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for label, rows in acs_cousub_2024.items():
        assert len(rows) >= 36000, f"ACS 2024 county subdivision {label} coverage too small"
        assert len({row["county_subdivision_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith("0600000US") and len(row.get("county_subdivision_geoid", "")) == 10 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for label, rows in acs_school_2024.items():
        assert len(rows) >= 10000, f"ACS 2024 school district {label} coverage too small"
        assert len({row["district_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith("9700000US") and len(row.get("district_geoid", "")) == 7 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for district_type, profiles, prefix, expected in (("elementary", acs_school_elementary_2024, "9500000US", 1978), ("secondary", acs_school_secondary_2024, "9600000US", 501)):
        for label, rows in profiles.items():
            assert len(rows) == expected, f"ACS 2024 {district_type} school district {label} coverage mismatch"
            assert len({row["district_geoid"] for row in rows}) == len(rows)
            assert all(row.get("GEO_ID", "").startswith(prefix) and len(row.get("district_geoid", "")) == 7 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for geo_type, profiles, prefix, expected in (("consolidated city", acs_consolidated_city_2024, "1700000US", 8), ("Alaska Native Regional Corporation", acs_anrc_2024, "2300000US", 12)):
        for label, rows in profiles.items():
            assert len(rows) == expected, f"ACS 2024 {geo_type} {label} coverage mismatch"
            assert len({row["geography_geoid"] for row in rows}) == len(rows)
            assert all(row.get("GEO_ID", "").startswith(prefix) and len(row.get("geography_geoid", "")) == 7 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for geo_type, profiles, prefix, expected, geoid_length in (("principal city", acs_principal_city_2024, "312M700US", 1294, 12), ("metropolitan division", acs_metropolitan_division_2024, "314M700US", 37, 10)):
        for label, rows in profiles.items():
            assert len(rows) == expected, f"ACS 2024 {geo_type} {label} coverage mismatch"
            assert len({row["geography_geoid"] for row in rows}) == len(rows)
            assert all(row.get("GEO_ID", "").startswith(prefix) and len(row.get("geography_geoid", "")) == geoid_length and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    special_specs = {
        "subminor_civil_division": ("0670000US", 145, 15),
        "tribal_subdivision_or_remainder": ("2510000US", 493, 7),
        "american_indian_area_reservation_statistical": ("2520000US", 617, 5),
        "off_reservation_trust_land_hawaiian_homeland": ("2540000US", 247, 5),
        "tribal_census_tract": ("2560000US", 493, 10),
        "tribal_block_group": ("2580000US", 935, 11),
    }
    for geo_type, profiles in acs_other_special_2024.items():
        prefix, expected, geoid_length = special_specs[geo_type]
        for label, rows in profiles.items():
            profile_expected = 0 if geo_type == "tribal_block_group" and label == "poverty" else expected
            assert len(rows) == profile_expected, f"ACS 2024 {geo_type} {label} coverage mismatch"
            assert len({row["geography_geoid"] for row in rows}) == len(rows)
            assert all(row.get("GEO_ID", "").startswith(prefix) and len(row.get("geography_geoid", "")) == geoid_length and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for label, rows in acs_tract_2024.items():
        assert len(rows) >= 85000, f"ACS 2024 tract {label} coverage too small"
        assert len({row["tract_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith("1400000US") and len(row.get("tract_geoid", "")) == 11 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for label, rows in acs_urban_2024.items():
        assert len(rows) >= 2600, f"ACS 2024 urban area {label} coverage too small"
        assert len({row["urban_area_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith("2690000US") and len(row.get("urban_area_geoid", "")) == 11 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for label, rows in acs_district_2024_5yr.items():
        assert len(rows) == 440, f"ACS 2024 five-year district {label} coverage mismatch"
        assert len({row["district_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith("5001900US") and len(row.get("district_geoid", "")) == 4 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for label, rows in acs_aiannh_2024.items():
        assert len(rows) == 704, f"ACS 2024 AIANNH {label} coverage mismatch"
        assert len({row["aiannh_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith("2500000US") and len(row.get("aiannh_geoid", "")) == 5 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for (chamber, label), rows in acs_state_legislative_2024.items():
        expected = 1964 if chamber == "upper" else 4879
        prefix = "610U900US" if chamber == "upper" else "620L900US"
        assert len(rows) == expected, (chamber, label, len(rows), expected)
        assert len({row["district_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith(prefix) and len(row.get("district_geoid", "")) == 5 and row.get("chamber") == chamber and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for label, rows in acs_cbsa_2024_5yr.items():
        assert len(rows) == 935, (label, len(rows))
        assert len({row["cbsa_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith("310M700US") and len(row.get("cbsa_geoid", "")) == 5 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    for label, rows in acs_csa_2024_5yr.items():
        assert len(rows) == 184, (label, len(rows))
        assert len({row["csa_geoid"] for row in rows}) == len(rows)
        assert all(row.get("GEO_ID", "").startswith("330M700US") and len(row.get("csa_geoid", "")) == 3 and row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)
    assert_unique(counties_2024, "GEOID", "2024 county GEOIDs")
    assert_unique(zctas_2024, "GEOID", "2024 ZCTA GEOIDs")
    assert_unique(cbsa_2024, "GEOID", "2024 CBSA GEOIDs")
    assert_unique(places_2024, "GEOID", "2024 place GEOIDs")
    assert_unique(tracts_2024, "GEOID", "2024 tract GEOIDs")
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
    for label, rows in (("education", acs_place_education), ("poverty", acs_place_poverty)):
        assert len(rows) >= 30000, f"ACS place {label} coverage too small"
        assert all(row.get("GEO_ID", "").startswith("1600000US") and row.get("place_fips") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS place {label} GEO_IDs"
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
    for label, rows in (("age_sex", acs_district_age_sex), ("education", acs_district_education), ("poverty", acs_district_poverty), ("income", acs_district_income), ("housing", acs_district_housing), ("race", acs_district_race)):
        assert len(rows) >= 400, f"too few ACS district {label} rows"
        assert all(row.get("GEO_ID", "").startswith("5001800US") and row.get("district_geoid") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["GEO_ID"] for row in rows}) == len(rows), f"duplicate ACS district {label} GEO_IDs"
    assert len(noaa_state_climate) >= 12000
    assert {row.get("parameter") for row in noaa_state_climate} == {"annual_avg_temperature_f", "annual_precipitation_inches"}
    assert len({row.get("state_abbr") for row in noaa_state_climate}) == 50
    assert all(row.get("year") and row.get("value") is not None and row.get("source") for row in noaa_state_climate)
    for label, rows in (("age_sex", acs_school_age_sex), ("education", acs_school_education), ("poverty", acs_school_poverty), ("income", acs_school_income), ("housing", acs_school_housing), ("race", acs_school_race)):
        assert len(rows) >= 10000, f"ACS school {label} coverage too small"
        assert all(row.get("GEO_ID", "").startswith("9700000US") and row.get("district_geoid") and row.get("state_fips") and row.get("source") for row in rows)
        assert len({row["district_geoid"] for row in rows}) == len(rows), f"duplicate ACS school {label} GEOIDs"
    for label, rows in (("age_sex", acs_cousub_age_sex), ("income", acs_cousub_income), ("poverty", acs_cousub_poverty), ("education", acs_cousub_education), ("housing", acs_cousub_housing), ("race", acs_cousub_race)):
        assert len(rows) >= 35000, f"ACS county subdivision {label} coverage too small"
        assert all(row.get("GEO_ID", "").startswith("0600000US") and row.get("county_subdivision_geoid") and len(row["county_subdivision_geoid"]) == 10 and row.get("source") for row in rows)
        assert len({row["county_subdivision_geoid"] for row in rows}) == len(rows), f"duplicate ACS county subdivision {label} GEOIDs"

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
    print(f"validated states={len(states)} counties={len(counties)} county_population={len(county_population)} places={len(places)} place_population={len(place_population)} legislators={len(legislators)} state_legislators={len(state_legislators)} fec_candidates={len(fec_candidates)} fec_committees={len(fec_committees)} fec_results={len(fec_results)} fec_federal_elections={len(fec_federal_elections)} fec_federal_elections_2020={len(fec_federal_elections_2020)} fec_federal_elections_2018={len(fec_federal_elections_2018)} fec_federal_elections_2016={len(fec_federal_elections_2016)} fec_federal_elections_2014={len(fec_federal_elections_2014)} fec_federal_elections_2012={len(fec_federal_elections_2012)} fec_federal_elections_2008={len(fec_federal_elections_2008)} fec_federal_elections_2006={len(fec_federal_elections_2006)} acs_district_education={len(acs_district_education)} acs_district_poverty={len(acs_district_poverty)} acs_district_income={len(acs_district_income)} acs_district_housing={len(acs_district_housing)} acs_district_race={len(acs_district_race)} governors={len(governors)} governor_terms={sum(len(row.get('terms', [])) for row in governors)} presidents={len(presidents)} vice_presidents={len(vice_presidents)} justices={len(justices)} current_justices={len(current_justices)} federal_judges={len(federal_judges)} secretaries_of_state={len(secretaries_of_state)} state_department_principals={len(state_department_principals)} acs_variables={len(acs_variables)} acs_state_age_sex={len(acs_state_age_sex)} acs_state_education={len(acs_state_education)} acs_state_poverty={len(acs_state_poverty)} acs_state_income={len(acs_state_income)} acs_state_housing={len(acs_state_housing)} acs_state_race={len(acs_state_race)} acs_county_age_sex={len(acs_county_age_sex)} acs_county_education={len(acs_county_education)} acs_county_poverty={len(acs_county_poverty)} acs_county_income={len(acs_county_income)} acs_county_housing={len(acs_county_housing)} acs_county_race={len(acs_county_race)} acs_place_age_sex={len(acs_place_age_sex)} acs_place_income={len(acs_place_income)} acs_place_housing={len(acs_place_housing)} acs_place_race={len(acs_place_race)} agencies={len(agencies)} executive_orders={len(executive_orders)} proclamations={len(proclamations)} presidential_documents={len(presidential_documents)} zctas={len(zctas)} relationships={len(relationships)} districts_2020={len(districts)} districts_2025={len(current_districts)}")


if __name__ == "__main__":
    main()
