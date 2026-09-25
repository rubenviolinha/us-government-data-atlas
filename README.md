# US Government Data Atlas

An open, versioned catalog of U.S. government, geographic, demographic, and historical officeholder data.

## Initial scope

- States and territories with stable identifiers
- Census population estimates
- Census geography and ZCTA references
- Historical senators and governors, with provenance
- Reproducible source snapshots and normalized releases

Every dataset should preserve its source URL, retrieval timestamp, source vintage, license, and transformation notes.

The current release contains 127 cataloged datasets, including 57 Census reference jurisdictions, 3,222 counties, 2020 and 2023 ZCTA geography, 85,396 tracts, 3,192 2023 county business-pattern totals, 35,002 2022 and 34,954 2023 ZIP Code Business Patterns totals, complete six-table ACS demographic profiles for 36,434 county subdivisions, 32,329 places, 13,333 school districts, complete six-table demographic profiles for 10,904 unified school districts, current and historical governor rosters, the current White House Cabinet roster, historical and current senator/representative views, historical and current state legislative chamber views, historical and current Supreme Court justice views, historical and current Article III federal judge views, explicit Federal Register agency hierarchy relationships, 6,844 state legislative districts, dated congressional districts, tribal areas, urban areas, CBSAs, PUMAs, district and place-level ACS demographic profiles, NOAA statewide climate history, and ZIP/PUMA/place/CBSA relationship and vintage-crosswalk tables.

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
python3 scripts/fetch_executive_orders.py
python3 scripts/fetch_proclamations.py
python3 scripts/fetch_presidential_documents.py
python3 scripts/fetch_vice_presidents.py
python3 scripts/fetch_supreme_court_justices.py
python3 scripts/fetch_federal_judges.py
python3 scripts/build_current_federal_judges.py
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

Then use `GET /health`, `GET /catalog`, or `GET /datasets/<filename>.json`, for example `/datasets/states.json`. Dataset endpoints also accept exact-match filters and pagination, such as `/datasets/states.json?abbr=CA`, `/datasets/counties_2023.json?STATEFP=06&limit=25`, or `/datasets/federal_judges.json?limit=20&offset=40`. The server is read-only and only serves files listed in `metadata/catalog.json`.

Exact-match filters are case-insensitive, and text containment filters use the `field__contains=value` form (for example, `/datasets/states.json?name__contains=land`). The API smoke tests run in CI with `python -m unittest tests/test_api.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for provenance, licensing, and refresh requirements. The repository code is MIT-licensed; dataset terms remain source-specific.

`metadata/release_manifest.json` fingerprints each normalized dataset with SHA-256 hashes for reproducible comparisons between releases.

To create a tabular export without adding duplicate files to Git, run `python3 scripts/export_csv.py states.json outputs/states.csv`. The exporter accepts only catalog-listed normalized datasets and serializes nested JSON values safely.

The legislator script imports current and historical congressional members and terms from the open `unitedstates/congress-legislators` project, retaining Bioguide and other government identifiers.

Historical election coverage includes FEC presidential results from 1984–2024, congressional result compilations from 2002–2022 plus 2010, and National Archives Electoral College tables for every election from 1789 through 2024. Legacy records retain source-page metadata and synthetic IDs where the original publication predates modern identifiers.
