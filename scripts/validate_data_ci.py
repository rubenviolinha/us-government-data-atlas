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

    print(f"CI validation passed: catalog={len(entries)} states={len(states)} FEMA declarations={len(disasters)}")


if __name__ == "__main__":
    main()
