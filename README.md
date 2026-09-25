# US Government Data Atlas

An open, versioned catalog of U.S. government, geographic, demographic, and historical officeholder data.

## Initial scope

- States and territories with stable identifiers
- Census population estimates
- Census geography and ZCTA references
- Historical senators and governors, with provenance
- Reproducible source snapshots and normalized releases

Every dataset should preserve its source URL, retrieval timestamp, source vintage, license, and transformation notes.

The current geography release includes 57 Census reference jurisdictions, 3,222 counties, 33,144 2020 ZCTAs, and 46,960 usable ZCTA-to-county intersections.

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

The legislator script imports current and historical congressional members and terms from the open `unitedstates/congress-legislators` project, retaining Bioguide and other government identifiers.
