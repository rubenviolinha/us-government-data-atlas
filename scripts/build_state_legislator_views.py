#!/usr/bin/env python3
"""Build upper- and lower-chamber views from the Open States roster."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"


def main():
    people = json.loads((DATA / "state_legislators_openstates.json").read_text(encoding="utf-8"))
    counts = {}
    for chamber in ("upper", "lower"):
        rows = []
        for person in people:
            if not any(role.get("type") == chamber for role in person.get("roles", [])):
                continue
            row = dict(person)
            row["chamber_scope"] = chamber
            rows.append(row)
        rows.sort(key=lambda row: row.get("id", ""))
        filename = f"state_legislators_{chamber}.json"
        (DATA / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        counts[filename] = len(rows)
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
