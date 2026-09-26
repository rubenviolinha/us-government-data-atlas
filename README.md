# US Government Data Atlas

An open, versioned catalog of U.S. government, geographic, demographic, and historical officeholder data.

## Initial scope

- States and territories with stable identifiers
- Census population estimates
- Census geography and ZCTA references
- Historical senators and governors, with provenance
- Reproducible source snapshots and normalized releases

Every dataset should preserve its source URL, retrieval timestamp, source vintage, license, and transformation notes.

The current release contains 653 cataloged datasets, including official 2024 presidential ballot candidates and House Clerk candidate-level 2024 congressional vote totals, 70,422 FEMA disaster-declaration summary records published as four repository-safe parts, compact six-table ACS 2024 1-year profiles for states, congressional districts, eligible counties, eligible places, and PUMAs, compact six-table ACS 2024 5-year profiles for the nation, regions, divisions, states, and PUMAs, plus household, labor, commuting, vehicle, internet, and rent-burden aggregate profiles for those same geographies, a 2024 ACS variable metadata catalog for all six profile tables, a compact four-part 2024 ACS 5-year population-and-housing profile for all 242,297 Census block groups, plus compact four-part education, income, race, household, labor, occupancy, commuting, vehicles, internet, rent-burden, income-distribution, median-age, median-rent, and rooms profiles for the same block groups, full-coverage six-table ACS 2024 5-year profiles for all counties and places, compact 2024 ACS 5-year county-subdivision, elementary-school-district, secondary-school-district, unified-school-district, consolidated-city, Alaska-Native-Regional-Corporation, principal-city, metropolitan-division, subminor-civil-division, tribal-subdivision, tribal reservation/statistical entity, off-reservation trust-land/Hawaiian homeland, tribal-census-tract, tribal-block-group, state-part, county-part, AIANNH-part, tribal tract/block-group part, tract, urban-area, congressional-district, AIANNH-area, state-legislative-district, CBSA, CSA, and ZCTA population/headline profiles, plus detailed income-distribution, median-age, median-gross-rent, and rooms profiles for all 33,772 ACS-covered ZCTAs, 3,222 counties, 32,330 ACS-covered places, 85,382 ACS-covered tracts (the tract tables are split into four parts each), 36,421 ACS-covered county subdivisions, and 1,978 elementary, 501 secondary, and 10,901 unified ACS-covered school districts, plus commuting, vehicle availability, internet access, and rent-burden profiles for all 3,222 counties, 32,330 ACS-covered places, 33,772 ACS-covered ZCTAs, 85,382 ACS-covered tracts (the tract tables are split into four parts each), 36,421 ACS-covered county subdivisions, 1,978 elementary, 501 secondary, and 10,901 unified ACS-covered school districts, 935 CBSAs, and 184 CSAs, a joined state/territory summary, CDC/ATSDR 2022 county, tract, and ZCTA social-vulnerability indicators, the complete public 2025 Census Gazetteer geography set (119th Congress, states, counties, places, tracts, ZCTAs, CBSAs, county subdivisions, school districts, tribal areas, urban areas, and state legislative districts), 2020-2025 Census population estimates for states, counties, places, CBSAs, and CSAs, 2024 and 2023 geography snapshots, 1,168 official 2024 FEC congressional ballot-candidate records, the FEC 2025 state/territory election-office directory, 2020 ZCTA geography, compact 2023 ACS 1-year and 5-year PUMA demographic profiles, 3,192 2023 county business-pattern totals, 925 2023 CBSA and 181 2023 CSA business-pattern totals, 35,002 2022 and 34,954 2023 ZIP Code Business Patterns totals, complete six-table ACS demographic profiles for 36,434 county subdivisions, 32,329 places, 13,333 school districts, current and historical governor rosters, the current White House Cabinet roster, historical and current senator/representative views, historical and current state legislative chamber views, historical and current Supreme Court justice views, historical and current Article III federal judge views, a derived index of federal courts represented in the FJC roster, explicit Federal Register agency hierarchy relationships, dated congressional districts, tribal areas, urban areas, CBSAs, PUMAs, district and place-level ACS demographic profiles, NOAA statewide and county climate history through 2025, and ZIP/PUMA/place/CBSA relationship and vintage-crosswalk tables.

## Repository layout

```text
data/raw/          Source snapshots (unmodified)
data/normalized/   Clean, query-friendly tables
metadata/          Source registry and schemas
scripts/            Reproducible ingestion scripts
```

## First run

```bash
python3 scripts/fetch_initial_data.py
python3 scripts/fetch_county_population.py
python3 scripts/fetch_place_population.py
python3 scripts/fetch_legislators.py
python3 scripts/fetch_governors.py
python3 scripts/fetch_presidents.py
python3 scripts/fetch_federal_register_agencies.py
python3 scripts/build_federal_agency_relationships.py
python3 scripts/fetch_zbp_totals.py
python3 scripts/fetch_zbp_2023_totals.py
python3 scripts/fetch_cbp_2023_county_totals.py
python3 scripts/fetch_cbp_2023_cbsa_totals.py
python3 scripts/fetch_cbp_2023_csa_totals.py
python3 scripts/fetch_acs_puma_profiles.py
python3 scripts/fetch_acs_puma_5yr_profiles.py
python3 scripts/fetch_acs_puma_2024_5yr_profiles.py
python3 scripts/fetch_acs_2024_5yr_aggregate_profiles.py
python3 scripts/fetch_acs_2024_variable_catalog.py
python3 scripts/fetch_acs_2024_5yr_block_group_profile.py
python3 scripts/fetch_acs_2024_5yr_block_group_demographics.py
python3 scripts/fetch_gazetteer_2024.py
python3 scripts/fetch_fec_2024_congressional_ballots.py
python3 scripts/fetch_fec_state_election_directory.py
python3 scripts/fetch_gazetteer_2025.py
python3 scripts/fetch_population_2025.py
python3 scripts/fetch_acs_2024_1yr_profiles.py
python3 scripts/fetch_fec_2024_presidential_ballots.py
python3 scripts/fetch_executive_orders.py
python3 scripts/fetch_proclamations.py
python3 scripts/fetch_presidential_documents.py
python3 scripts/fetch_vice_presidents.py
python3 scripts/fetch_supreme_court_justices.py
python3 scripts/fetch_federal_judges.py
python3 scripts/build_current_federal_judges.py
python3 scripts/build_federal_court_index.py
python3 scripts/fetch_acs_2024_5yr_county_place_profiles.py
python3 scripts/fetch_acs_2024_5yr_cousub_profiles.py
python3 scripts/fetch_acs_2024_5yr_school_profiles.py
python3 scripts/fetch_acs_2024_5yr_special_geographies.py
python3 scripts/fetch_acs_2024_5yr_tract_profiles.py
python3 scripts/fetch_acs_2024_5yr_urban_profiles.py
python3 scripts/fetch_acs_2024_5yr_district_profiles.py
python3 scripts/fetch_acs_2024_5yr_aiannh_profiles.py
python3 scripts/fetch_acs_2024_5yr_state_legislative_profiles.py
python3 scripts/fetch_acs_2024_5yr_cbsa_profiles.py
python3 scripts/fetch_acs_2024_5yr_csa_profiles.py
python3 scripts/build_state_summary.py
python3 scripts/build_coverage_report.py
python3 scripts/fetch_cdc_svi_2022_counties.py
python3 scripts/fetch_cdc_svi_2022_tracts.py
python3 scripts/fetch_cdc_svi_2022_zctas.py
python3 scripts/fetch_zcta_acs_2024.py
python3 scripts/fetch_current_cabinet.py
python3 scripts/fetch_secretaries_of_state.py
python3 scripts/fetch_state_department_principals.py
python3 scripts/build_catalog.py
python3 scripts/fetch_geography.py
python3 scripts/fetch_gnis.py
python3 scripts/fetch_districts.py
python3 scripts/validate_data.py
python3 scripts/validate_capitals.py
```

The scripts use public Census endpoints and write retrieval manifests alongside the downloaded data. State capitals are included as an explicitly marked initial reference while state-government validation is added.

The GNIS script downloads the compact Government Units and Populated Places extracts (states, counties, cities, and other named places) rather than the much larger all-names archive.

The district script extracts compact attribute tables from the 2020 and current 2025 TIGER congressional-district archives; the source archives remain available for geometry consumers.

The validator checks identifier uniqueness and cross-references between states, counties, places, ZCTAs, relationships, and districts. It also runs in GitHub Actions on pushes and pull requests.

The capital validator reconciles the initial capital list to Census places and explicitly flags island jurisdictions and naming exceptions for official state-government review.

## Access handoff

`metadata/access_requirements.json` records the remaining external requirements: Census ACS credentials or bulk-file approval and USPS licensing for exact ZIP delivery geography. State-legislator history uses the public Open States people repository, and a 2024 FEC candidate master snapshot is available as keyless bulk data; FEC API access is only needed for transaction-level or broader election-result ingestion.

The ACS profile variable catalog is available at `data/normalized/acs_profile_variables_2023.json`; it includes labels and concepts for DP02, DP03, DP04, and DP05 even though value queries remain credential-gated in this environment.

The keyless summary-file fallback `data/normalized/acs_state_age_sex_2023.json` contains state-level 2023 ACS 5-year B01001 age/sex estimates, with matching county-level profiles, place-level B19013/B25001/B02001 profiles, and 2023 ACS 1-year congressional-district profiles now included.

Additional keyless ACS state profiles are available for B19013 income, B25001 housing units, and B02001 race in `data/normalized/`; the county files use the same public summary-file source and preserve estimates and margins of error.

## Local API

The checked-in releases can be queried locally without an API key:

```bash
python3 api/server.py
```

Then use `GET /health`, `GET /catalog`, `GET /sources`, `GET /access-requirements`, or `GET /datasets/<filename>.json`, for example `/datasets/states.json`. Dataset endpoints also accept exact-match filters and pagination, such as `/datasets/states.json?abbr=CA`, `/datasets/counties_2023.json?STATEFP=06&limit=25`, or `/datasets/federal_judges.json?limit=20&offset=40`. The server is read-only and only serves files listed in `metadata/catalog.json`.

Exact-match filters are case-insensitive, and text containment filters use the `field__contains=value` form (for example, `/datasets/states.json?name__contains=land`). The API smoke tests run in CI with `python -m unittest tests/test_api.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for provenance, licensing, and refresh requirements. The repository code is MIT-licensed; dataset terms remain source-specific.

`metadata/release_manifest.json` fingerprints each normalized dataset with SHA-256 hashes for reproducible comparisons between releases.

To create a tabular export without adding duplicate files to Git, run `python3 scripts/export_csv.py states.json outputs/states.csv`. The exporter accepts only catalog-listed normalized datasets and serializes nested JSON values safely.

The legislator script imports current and historical congressional members and terms from the open `unitedstates/congress-legislators` project, retaining Bioguide and other government identifiers.

Historical election coverage includes FEC presidential results from 1984–2024, congressional result compilations from 2002–2022 plus 2010, and National Archives Electoral College tables for every election from 1789 through 2024. Legacy records retain source-page metadata and synthetic IDs where the original publication predates modern identifiers.
