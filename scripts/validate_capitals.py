#!/usr/bin/env python3
"""Reconcile the initial capital reference with Census place records."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"

# Census place names use jurisdiction-specific conventions for these capitals.
ALIASES = {
    "HI": "Urban Honolulu CDP",
    "MN": "St. Paul city",
    "TN": "Nashville-Davidson metropolitan government (balance)",
}


def main():
    states = json.loads((DATA / "states.json").read_text(encoding="utf-8"))
    places = json.loads((DATA / "places_2020.json").read_text(encoding="utf-8"))
    result = []
    for state in states:
        capital = state.get("capital")
        candidates = [
            place for place in places
            if place.get("USPS") == state["abbr"]
            and capital
            and place.get("NAME", "").lower().startswith(capital.lower() + " ")
        ]
        status = "matched" if candidates else "needs_review"
        alias = ALIASES.get(state["abbr"])
        if not candidates and alias:
            candidates = [place for place in places if place.get("USPS") == state["abbr"] and place.get("NAME") == alias]
            if candidates:
                status = "alias_match"
        result.append({
            "abbr": state["abbr"],
            "state_name": state["name"],
            "capital": capital,
            "status": status,
            "candidate_place_geoids": [place["GEOID"] for place in candidates[:5]],
            "note": "Census place reconciliation only; official state-government validation remains required." if status != "matched" else "Census place name match; official state-government validation remains recommended."
        })
    (DATA / "capital_validation.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {}
    for row in result:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(json.dumps({"records": len(result), "status_counts": counts}, indent=2))


if __name__ == "__main__":
    main()
