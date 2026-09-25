#!/usr/bin/env python3
"""Build a joined state/territory summary from validated normalized releases."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
SOURCE = "https://github.com/rubenviolinha/us-government-data-atlas"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main():
    states = load("states.json")
    population = {row["state_fips"]: row for row in load("state_population_2020_2025.json")}
    governors = {row["state"]: row for row in load("current_governors_nga.json")}
    counties = {}
    for row in load("counties_2025.json"):
        counties[row["GEOID"][:2]] = counties.get(row["GEOID"][:2], 0) + 1
    places = {}
    for row in load("places_2025.json"):
        places[row["GEOID"][:2]] = places.get(row["GEOID"][:2], 0) + 1
    zctas = {}
    for row in load("zctas_2025.json"):
        zctas[row["GEOID"][:2]] = zctas.get(row["GEOID"][:2], 0) + 1
    senators = {}
    for row in load("current_senators.json"):
        for term in row.get("terms", []):
            senators.setdefault(term.get("state"), []).append(row.get("name", {}).get("official_full") or row.get("name", {}).get("first", "") + " " + row.get("name", {}).get("last", ""))
    representatives = {}
    for row in load("current_representatives.json"):
        for term in row.get("terms", []):
            representatives.setdefault(term.get("state"), []).append(row.get("name", {}).get("official_full") or row.get("name", {}).get("first", "") + " " + row.get("name", {}).get("last", ""))
    rows = []
    for state in states:
        fips = state["state_fips"]
        abbr = state["abbr"]
        pop = population.get(fips, {})
        governor = governors.get(state["name"], {})
        rows.append({
            "state_fips": fips,
            "abbr": abbr,
            "state_name": state["name"],
            "capital": state.get("capital"),
            "population_2025": pop.get("population_2025"),
            "population_source": pop.get("source_vintage"),
            "governor": governor.get("name"),
            "governor_profile_url": governor.get("profile_url"),
            "senators": sorted(set(senators.get(abbr, []))),
            "representative_count": len(set(representatives.get(abbr, []))),
            "county_count": counties.get(fips, 0),
            "place_count": places.get(fips, 0),
            "zcta_count": zctas.get(fips, 0),
            "source": SOURCE,
        })
    output = DATA / "state_summary.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(output.relative_to(ROOT)), "records": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
