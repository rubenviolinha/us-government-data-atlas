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

    print(f"CI validation passed: catalog={len(entries)} states={len(states)} FEMA declarations={len(disasters)} PLACES county rows={len(places)} ZCTA rows={len(zcta_places)} place rows={len(named_places)} NCES schools={len(schools)}")


if __name__ == "__main__":
    main()
