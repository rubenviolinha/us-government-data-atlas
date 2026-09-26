#!/usr/bin/env python3
"""Fast CI validation for the checked-in data catalog.

The full validator intentionally walks every normalized record, which is useful
for local audits but now exceeds the hosted runner's practical time budget for
this multi-gigabyte catalog.  CI keeps the inexpensive catalog-wide checks and
deep-checks the newest/high-risk feeds.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    catalog = read_json(ROOT / "metadata/catalog.json")
    release = read_json(ROOT / "metadata/release_manifest.json")
    entries = catalog.get("entries", [])
    assert entries, "catalog is empty"
    assert len(entries) == release.get("dataset_count") == len(release.get("datasets", [])), "catalog/release entry count mismatch"

    for entry in entries:
        path = ROOT / entry["file"]
        assert path.is_file(), f"missing catalog file: {entry['file']}"
        assert path.stat().st_size == entry["size_bytes"], f"size mismatch: {entry['file']}"
        assert entry.get("records", 0) >= 0

    states = read_json(ROOT / "data/normalized/states.json")
    assert len(states) >= 50
    assert len({row["abbr"] for row in states}) == len(states)

    # Deep-check the newest ACS access profiles added in the latest release.
    for geography, expected in (("cbsa", 935), ("csa", 184)):
        for label in ("commuting", "vehicles", "internet", "rent_burden"):
            rows = read_json(ROOT / f"data/normalized/acs_{geography}_{label}_2024_5yr.json")
            assert len(rows) == expected, f"unexpected {geography} {label} row count"
            assert len({row[geography] for row in rows}) == expected
            assert all(row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)

    for geography, expected in (("us", 1), ("region", 4), ("division", 9), ("state", 52)):
        for label in ("households", "labor", "commuting", "vehicles", "internet", "rent_burden"):
            rows = read_json(ROOT / f"data/normalized/acs_{geography}_{label}_2024_5yr.json")
            assert len(rows) == expected, f"unexpected {geography} {label} row count"
            assert len({row["geography_geoid"] for row in rows}) == expected
            assert all(row.get("source") and row.get("vintage") == "2024 ACS 5-year" for row in rows)

    disasters = []
    for path in sorted((ROOT / "data/normalized").glob("fema_disaster_declarations_part*.json")):
        disasters.extend(read_json(path))
    assert len(disasters) >= 70000
    assert len({row["id"] for row in disasters}) == len(disasters)
    assert all(row.get("disasterNumber") and row.get("state") and row.get("incidentType") for row in disasters)

    places = []
    for path in sorted((ROOT / "data" / "normalized").glob("cdc_places_counties_2024_part*.json")):
        places.extend(read_json(path))
    assert len(places) >= 240000
    assert len({row["locationid"] for row in places}) >= 3100
    assert len({(row["locationid"], row["measureid"], row["data_value_type"]) for row in places}) == len(places)
    assert all(row.get("source") and row.get("vintage") for row in places)

    zcta_places = []
    for path in sorted((ROOT / "data" / "normalized").glob("cdc_places_zctas_2024_part*.json")):
        zcta_places.extend(read_json(path))
    assert len(zcta_places) >= 1200000
    assert len({row["locationid"] for row in zcta_places}) >= 30000
    assert len({(row["locationid"], row["measureid"], row["data_value_type"]) for row in zcta_places}) == len(zcta_places)
    assert all(row.get("source") and row.get("vintage") for row in zcta_places)

    named_places = []
    for path in sorted((ROOT / "data" / "normalized").glob("cdc_places_named_places_2024_part*.json")):
        named_places.extend(read_json(path))
    assert len(named_places) >= 2200000
    assert len({row["locationid"] for row in named_places}) >= 29000
    assert len({(row["locationid"], row["measureid"], row["data_value_type"]) for row in named_places}) == len(named_places)
    assert all(row.get("source") and row.get("vintage") for row in named_places)

    schools = []
    for path in sorted((ROOT / "data" / "normalized").glob("nces_public_schools_2024_25_part*.json")):
        schools.extend(read_json(path))
    assert len(schools) >= 100000
    assert len({row["ncessch"] for row in schools}) == len(schools)
    assert all(row.get("ncessch") and row.get("leaid") and row.get("sch_name") for row in schools)
    assert all(row.get("source") and row.get("vintage") == "2024-25 CCD public school universe" for row in schools)

    districts = read_json(ROOT / "data/normalized/nces_public_districts_2024_25.json")
    assert len(districts) >= 19000
    assert len({row["leaid"] for row in districts}) == len(districts)
    assert all(row.get("leaid") and row.get("lea_name") and row.get("source") for row in districts)
    assert all(row.get("vintage") == "2024-25 CCD public LEA universe" for row in districts)

    private_schools = read_json(ROOT / "data/normalized/nces_private_schools_2023_24.json")
    assert len(private_schools) >= 22000
    assert len({row["ppin"] for row in private_schools}) == len(private_schools)
    assert all(row.get("ppin") and row.get("pinst") and row.get("source") for row in private_schools)
    assert all(row.get("vintage") == "2023-24 PSS public-use file" for row in private_schools)

    register = []
    for path in sorted((ROOT / "data" / "normalized").glob("nps_national_register_listed_2026_part*.json")):
        register.extend(read_json(path))
    assert len(register) >= 100000
    assert len({(row["ref_number"], row.get("property_name"), row.get("listed_date"), row.get("status"), row.get("request_type")) for row in register}) == len(register)
    assert all(row.get("ref_number") and row.get("property_name") and row.get("state") for row in register)
    assert all(row.get("source") and row.get("vintage") == "NPS National Register listed properties through 2026-05-22" for row in register)

    svi_counties = read_json(ROOT / "data/normalized/svi_counties_2022.json")
    assert len(svi_counties) >= 3100
    assert len({row["GEOID"] for row in svi_counties}) == len(svi_counties)
    assert all(row.get("GEOID") and row.get("source") and row.get("vintage") == "CDC/ATSDR SVI 2022" for row in svi_counties)
    svi_tracts = []
    for path in sorted((ROOT / "data" / "normalized").glob("svi_tracts_2022_part*.json")):
        svi_tracts.extend(read_json(path))
    assert len(svi_tracts) >= 84000
    assert len({row["GEOID"] for row in svi_tracts}) == len(svi_tracts)
    svi_zctas = read_json(ROOT / "data/normalized/svi_zctas_2022.json")
    assert len(svi_zctas) >= 33000
    assert len({row["GEOID"] for row in svi_zctas}) == len(svi_zctas)
    assert all(row.get("source") and row.get("comparison") == "national" for row in svi_zctas)

    aviation = read_json(ROOT / "data/normalized/bts_aviation_facilities.json")
    assert len(aviation) >= 19000
    assert len({(row["site_no"], row.get("arpt_id")) for row in aviation}) == len(aviation)
    assert all(row.get("site_no") and row.get("arpt_name") and (row.get("state_name") or row.get("country_code")) for row in aviation)
    assert all(row.get("source") and row.get("vintage") == "FAA-updated USDOT/BTS Aviation Facilities" for row in aviation)

    earthquakes = read_json(ROOT / "data/normalized/usgs_earthquakes_past_week.json")
    assert len(earthquakes) >= 1000
    assert len({row["id"] for row in earthquakes}) == len(earthquakes)
    assert all(row.get("id") and row.get("event_type") for row in earthquakes)
    assert all(row.get("source") and row.get("vintage") == "USGS all earthquakes past week rolling feed" for row in earthquakes)
    assert all(-180 <= row["longitude"] <= 180 and -90 <= row["latitude"] <= 90 for row in earthquakes if row.get("longitude") is not None and row.get("latitude") is not None)

    tide_stations = read_json(ROOT / "data/normalized/noaa_tide_stations.json")
    assert len(tide_stations) >= 250
    assert len({row["station_id"] for row in tide_stations}) == len(tide_stations)
    assert all(row.get("station_id") and row.get("name") and row.get("source") for row in tide_stations)
    assert all(row.get("vintage") == "NOAA tide and water-level station metadata registry" for row in tide_stations)
    assert all(-180 <= row["longitude"] <= 180 and -90 <= row["latitude"] <= 90 for row in tide_stations)

    nws_entry = next(entry for entry in entries if entry["file"] == "data/normalized/nws_stations.json")
    assert nws_entry["records"] >= 10000
    assert nws_entry["size_bytes"] >= 30000000

    zcta_place_relationships = read_json(ROOT / "data/normalized/zcta_place_relationships_2020.json")
    assert len(zcta_place_relationships) >= 50000
    assert len({(row["zcta"], row["place"]) for row in zcta_place_relationships}) == len(zcta_place_relationships)
    assert len({row["zcta"] for row in zcta_place_relationships}) >= 25000
    assert len({row["place"] for row in zcta_place_relationships}) >= 20000
    assert all(row.get("source") and row.get("vintage") == "2020 Census ZCTA-to-place relationship file" for row in zcta_place_relationships)

    zcta_tract_relationships = []
    for path in sorted((ROOT / "data/normalized").glob("zcta_tract_relationships_2020_part*.json")):
        zcta_tract_relationships.extend(read_json(path))
    assert len(zcta_tract_relationships) >= 160000
    assert len({(row["zcta"], row["tract"]) for row in zcta_tract_relationships}) == len(zcta_tract_relationships)
    assert len({row["zcta"] for row in zcta_tract_relationships}) >= 30000
    assert len({row["tract"] for row in zcta_tract_relationships}) >= 80000
    assert all(row.get("source") and row.get("vintage") == "2020 Census ZCTA-to-tract relationship file" for row in zcta_tract_relationships)

    tract_puma_relationships = read_json(ROOT / "data/normalized/tract_puma_relationships_2020.json")
    assert len(tract_puma_relationships) >= 85000
    assert len({row["tract"] for row in tract_puma_relationships}) >= 80000
    assert len({row["puma"] for row in tract_puma_relationships}) >= 2000
    assert len({(row["tract"], row["puma"]) for row in tract_puma_relationships}) == len(tract_puma_relationships)
    assert all(row.get("source") and row.get("vintage") == "2020 Census tract-to-PUMA relationship file" for row in tract_puma_relationships)

    water_sites = read_json(ROOT / "data/normalized/usgs_active_stream_sites.json")
    assert len(water_sites) >= 11000
    assert len({row["site_no"] for row in water_sites}) == len(water_sites)
    assert len({row["state_fips"] for row in water_sites}) >= 50
    assert all(row.get("site_no") and row.get("station_name") for row in water_sites)
    assert all(row.get("source") and row.get("vintage") == "USGS active stream sites with instantaneous data" for row in water_sites)
    assert all(-180 <= row["longitude"] <= 180 and -90 <= row["latitude"] <= 90 for row in water_sites)

    print(f"CI validation passed: catalog={len(entries)} states={len(states)} FEMA declarations={len(disasters)} PLACES county rows={len(places)} ZCTA rows={len(zcta_places)} place rows={len(named_places)} NCES schools={len(schools)} NCES districts={len(districts)} NCES private schools={len(private_schools)} NPS register={len(register)} SVI counties={len(svi_counties)} tracts={len(svi_tracts)} ZCTAs={len(svi_zctas)} aviation={len(aviation)} earthquakes={len(earthquakes)} tide_stations={len(tide_stations)} nws_stations={nws_entry['records']} zcta_place={len(zcta_place_relationships)} zcta_tract={len(zcta_tract_relationships)} tract_puma={len(tract_puma_relationships)} usgs_stream_sites={len(water_sites)}")


if __name__ == "__main__":
    main()
