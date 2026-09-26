# Next session handoff

## Current state

- Repository: `rubenviolinha/us-government-data-atlas`
- Public API documentation: <https://rubenviolinha.github.io/us-government-data-atlas/>
- Current catalog: 1,022 normalized dataset files and 170 source-registry entries.
- Latest commit: `3947ba8` (`Make API docs more literal and complete`).
- The working tree was clean after the last push.
- Local data, capital, API, and documentation validators passed.

## What is already covered

The no-key release includes geography, states and capitals, population and demographics, governors and state legislators, senators and representatives, elections, federal offices, schools, public health, safety, climate, environment, transportation, and economic data. The API and searchable catalog are documented on GitHub Pages.

## Remaining gated work

1. USPS-authorized exact ZIP/address and delivery-point reference data.
2. Census API credentials only for arbitrary custom table/geography queries beyond the checked-in bulk snapshots.
3. Additional state-specific archival office histories where no stable public bulk source exists.

Do not put credentials in Git or chat. Use local environment secrets or authorized files.

## Suggested next-session order

1. Check the rolling public feeds and refresh any stale releases.
2. Compare Senate and NGA historical rosters against the normalized senator/governor datasets and record any gaps.
3. Choose a small first batch of state archival histories and document source-by-source provenance.
4. If credentials or licensed files are available, handle the three gated inputs above.
5. Run the full validators and update the Linear project with the resulting commit and release status.

## Official source references reviewed

- Senate chronological list, 1789-present: <https://www.senate.gov/artandhistory/history/resources/pdf/chronlist.pdf>
- National Governors Association former-governor archive: <https://www.nga.org/former-governors/>
- National Governors Association searchable index: <https://www.nga.org/former-governors/search/>
- Census ZCTA guidance and ZIP/ZCTA distinction: <https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html>
- Census 2024 geography products: <https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html>
