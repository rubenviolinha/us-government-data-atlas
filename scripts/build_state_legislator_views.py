#!/usr/bin/env python3
"""Build upper- and lower-chamber views from the Open States roster."""

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"


def main():
    people = json.loads((DATA / "state_legislators_openstates.json").read_text(encoding="utf-8"))
    counts = {}
    as_of = date.today().isoformat()
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
        current_rows = []
        for person in rows:
            if any(role.get("type") == chamber and (not role.get("end_date") or role.get("end_date") >= as_of) and role.get("start_date", "") <= as_of for role in person.get("roles", [])):
                row = dict(person)
                row["view_as_of"] = as_of
                current_rows.append(row)
        current_filename = f"current_state_legislators_{chamber}.json"
        (DATA / current_filename).write_text(json.dumps(current_rows, indent=2) + "\n", encoding="utf-8")
        counts[current_filename] = len(current_rows)
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
