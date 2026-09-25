#!/usr/bin/env python3
"""Build searchable senator and representative views from the canonical roster."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
SOURCE = "https://github.com/unitedstates/congress-legislators"


def main():
    people = json.loads((DATA / "congressional_legislators.json").read_text(encoding="utf-8"))
    outputs = {
        "senators.json": "sen",
        "representatives.json": "rep",
    }
    counts = {}
    for filename, office_type in outputs.items():
        rows = []
        for person in people:
            if not any(term.get("type") == office_type for term in person.get("terms", [])):
                continue
            row = dict(person)
            row["office_scope"] = "senator" if office_type == "sen" else "representative"
            row["source"] = SOURCE
            row["derived_from"] = "data/normalized/congressional_legislators.json"
            rows.append(row)
        rows.sort(key=lambda row: row.get("id", {}).get("bioguide", ""))
        (DATA / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        counts[filename] = len(rows)
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
