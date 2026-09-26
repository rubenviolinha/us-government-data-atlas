# US Government Data Atlas

An open, versioned catalog of U.S. government, geographic, demographic, and historical officeholder data.

## Initial scope

- States and territories with stable identifiers
- Census population estimates
- Census geography and ZCTA references
- Historical senators and governors, with provenance
- Reproducible source snapshots and normalized releases

Every dataset should preserve its source URL, retrieval timestamp, source vintage, license, and transformation notes.

The current release contains 729 cataloged datasets, including official 2024 presidential ballot candidates and House Clerk candidate-level 2024 congressional vote totals, 70,422 FEMA disaster-declaration summary records published as four repository-safe parts, compact six-table ACS 2024 1-year profiles for states, congressional districts, eligible counties, eligible places, and PUMAs, compact six-table ACS 2024 5-year profiles for the nation, regions, divisions, states, and PUMAs, plus household, labor, commuting, vehicle, internet, and rent-burden aggregate profiles for those same geographies, a 2024 ACS variable metadata catalog for all six profile tables, a compact four-part 2024 ACS 5-year population-and-housing profile for all 242,297 Census block groups, plus compact four-part education, income, race, household, labor, occupancy, commuting, vehicles, internet, rent-burden, income-distribution, median-age, median-rent, and rooms profiles for the same block groups, full-coverage six-table ACS 2024 5-year profiles for all counties and places, compact 2024 ACS 5-year county-subdivision, elementary-school-district, secondary-school-district, unified-school-district, consolidated-city, Alaska-Native-Regional-Corporation, principal-city, metropolitan-division, subminor-civil-division, tribal-subdivision, tribal reservation/statistical entity, off-reservation trust-land/Hawaiian homeland, tribal-census-tract, tribal-block-group, state-part, county-part, AIANNH-part, tribal tract/block-group part, tract, urban-area, congressional-district, AIANNH-area, state-legislative-district, CBSA, CSA, and ZCTA population/headline profiles, plus detailed income-distribution, median-age, median-gross-rent, and rooms profiles for all 33,772 ACS-covered ZCTAs, 3,222 counties, 32,330 ACS-covered places, 85,382 ACS-covered tracts (the tract tables are split into four parts each), 36,421 ACS-covered county subdivisions, and 1,978 elementary, 501 secondary, and 10,901 unified ACS-covered school districts, plus commuting, vehicle availability, internet access, and rent-burden profiles for all 3,222 counties, 32,330 ACS-covered places, 33,772 ACS-covered ZCTAs, 85,382 ACS-covered tracts (the tract tables are split into four parts each), 36,421 ACS-covered county subdivisions, 1,978 elementary, 501 secondary, and 10,901 unified ACS-covered school districts, 935 CBSAs, and 184 CSAs, a joined state/territory summary, CDC/ATSDR 2022 county, tract, and ZCTA social-vulnerability indicators plus CDC PLACES 2024 county and ZCTA health-indicator estimates, the complete public 2025 Census Gazetteer geography set (119th Congress, states, counties, places, tracts, ZCTAs, CBSAs, county subdivisions, school districts, tribal areas, urban areas, and state legislative districts), 2020-2025 Census population estimates for states, counties, places, CBSAs, and CSAs, 2024 and 2023 geography snapshots, 1,168 official 2024 FEC congressional ballot-candidate records, the FEC 2025 state/territory election-office directory, 2020 ZCTA geography, compact 2023 ACS 1-year and 5-year PUMA demographic profiles, 3,192 2023 county business-pattern totals, 925 2023 CBSA and 181 2023 CSA business-pattern totals, 35,002 2022 and 34,954 2023 ZIP Code Business Patterns totals, complete six-table ACS demographic profiles for 36,434 county subdivisions, 32,329 places, 13,333 school districts, current and historical governor rosters, the current White House Cabinet roster, historical and current senator/representative views, historical and current state legislative chamber views, historical and current Supreme Court justice views, historical and current Article III federal judge views, a derived index of federal courts represented in the FJC roster, explicit Federal Register agency hierarchy relationships, dated congressional districts, tribal areas, urban areas, CBSAs, PUMAs, district and place-level ACS demographic profiles, NOAA statewide and county climate history through 2025, ZIP/PUMA/place/CBSA relationship and vintage-crosswalk tables, a rolling USGS past-week earthquake snapshot with event metadata and coordinates, NOAA tide/water-level station metadata with locations, time zones, and monitoring capabilities, a National Weather Service station registry with identifiers, locations, elevation, providers, and linked forecast zones, the official 2020 Census ZCTA-to-place crosswalk with area-overlap fields, and the official 2020 Census ZCTA-to-tract crosswalk with area-overlap fields published as four repository-safe parts.

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
python3 scripts/fetch_bts_aviation_facilities.py
python3 scripts/fetch_usgs_earthquakes.py
python3 scripts/fetch_noaa_tide_stations.py
python3 scripts/fetch_nws_stations.py
python3 scripts/fetch_zcta_place_relationships.py
python3 scripts/fetch_zcta_tract_relationships.py
python3 scripts/fetch_tract_puma_relationships.py
python3 scripts/fetch_cdc_places_2024_counties.py
python3 scripts/fetch_cdc_places_2024_zctas.py
python3 scripts/fetch_cdc_places_2024_places.py
python3 scripts/fetch_nces_public_school_directory.py
python3 scripts/fetch_nces_public_district_directory.py
python3 scripts/fetch_nces_private_school_universe.py
python3 scripts/fetch_nps_national_register.py
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

CDC PLACES 2024 county, ZCTA, and named-place releases are included as long-form, sharded datasets with model-based health estimates, confidence limits, measure metadata, and CDC provenance. They use public Socrata bulk access and do not require an API key.

The NCES Common Core of Data 2024-25 public-school universe is included as two sharded JSON datasets with 101,333 school records, NCES and district identifiers, names, addresses, contacts, status, school type, charter flags, and grade ranges. It is a public downloadable ZIP release and does not require an API key.

The matching NCES 2024-25 public local education agency universe is also included, with 19,484 district records and district-level identifiers, contacts, administrative status, type, charter flag, grade range, and operational-school counts.

The NCES 2023-24 Private School Universe Survey public-use file is included with 22,510 private-school records, identifiers, addresses, coordinates, county and legislative geography, enrollment, staffing, school characteristics, and selected demographic percentages.

The National Park Service National Register of Historic Places listed-properties release is included as four JSON parts covering 100,866 records through 2026-05-22, with reference numbers, names, jurisdictions, addresses, dates, status, categories, significance, acreage, and archival links.

CDC/ATSDR Social Vulnerability Index 2022 releases are included for counties, census tracts, and ZCTAs: 3,144 county records, 84,120 tract records, and 33,642 ZCTA records with socioeconomic, household, housing, health-access, theme, and percentile fields. These ArcGIS bulk queries are public and do not require an API key.

The USDOT/Bureau of Transportation Statistics FAA-updated Aviation Facilities layer is included with 19,411 airport and aviation-facility records, identifiers, jurisdictions, ownership/use, coordinates, elevation, status, and contact fields. It is fetched from a public ArcGIS endpoint without an API key.

The USGS past-week earthquake snapshot is included as a rolling public GeoJSON release with magnitudes, event times, tsunami flags, significance, coordinates, depth, and event links. It is fetched from the USGS public feed without an API key; retrieval and feed-generation timestamps are preserved.

The NOAA tide and water-level station registry is included with station identifiers, names, locations, state, time zone, monitoring capabilities, and station links. It is fetched from NOAA's public metadata endpoint without an API key.

The National Weather Service station registry is included with observation-station identifiers, names, coordinates, elevation, time zones, providers, and linked forecast, county, and fire-weather zones. It is fetched from the public weather.gov API with a descriptive User-Agent and no API key.

The 2020 Census ZCTA-to-place relationship file is included with 2020 ZCTA and place identifiers, names, and land/water area-overlap fields. It is a public Census bulk file and does not require an API key.

The 2020 Census ZCTA-to-tract relationship file is included with 2020 ZCTA and tract identifiers, names, and land/water area-overlap fields. It is a public Census bulk file and does not require an API key.

The 2020 Census tract-to-PUMA relationship file is included with 85,452 tract-to-PUMA mappings keyed by 2020 Census GEOIDs. It is a public Census bulk file and does not require an API key.

## Local API

The checked-in releases can be queried locally without an API key:

```bash
python3 api/server.py
```

Then use `GET /health`, `GET /catalog`, `GET /dataset-groups`, `GET /dataset-groups/<group>`, `GET /sources`, `GET /access-requirements`, or `GET /datasets/<filename>.json`, for example `/datasets/states.json`. Dataset endpoints also accept exact-match filters and pagination, such as `/datasets/states.json?abbr=CA`, `/datasets/counties_2023.json?STATEFP=06&limit=25`, or `/datasets/federal_judges.json?limit=20&offset=40`. `/dataset-groups` combines repository-safe `_partN` shards into logical datasets and reports their aggregate record counts; `/dataset-groups/<group>` applies the same filters and pagination across all shards. The server is read-only and only serves files listed in `metadata/catalog.json`.

Exact-match filters are case-insensitive, and text containment filters use the `field__contains=value` form (for example, `/datasets/states.json?name__contains=land`). The API smoke tests run in CI with `python -m unittest tests/test_api.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for provenance, licensing, and refresh requirements. The repository code is MIT-licensed; dataset terms remain source-specific.

`metadata/release_manifest.json` fingerprints each normalized dataset with SHA-256 hashes for reproducible comparisons between releases.

To create a tabular export without adding duplicate files to Git, run `python3 scripts/export_csv.py states.json outputs/states.csv`. The exporter accepts only catalog-listed normalized datasets and serializes nested JSON values safely.

The legislator script imports current and historical congressional members and terms from the open `unitedstates/congress-legislators` project, retaining Bioguide and other government identifiers.

Historical election coverage includes FEC presidential results from 1984–2024, congressional result compilations from 2002–2022 plus 2010, and National Archives Electoral College tables for every election from 1789 through 2024. Legacy records retain source-page metadata and synthetic IDs where the original publication predates modern identifiers.
