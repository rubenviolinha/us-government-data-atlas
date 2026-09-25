#!/usr/bin/env python3
"""Build explicit parent/child relationships from the Federal Register agency catalog."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"


def main():
    agencies = json.loads((DATA / "federal_register_agencies.json").read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in agencies}
    relationships = []
    for child in agencies:
        parent_id = child.get("parent_id")
        if parent_id is None or parent_id not in by_id:
            continue
        parent = by_id[parent_id]
        relationships.append({
            "parent_id": parent["id"],
            "parent_name": parent.get("name"),
            "parent_slug": parent.get("slug"),
            "child_id": child["id"],
            "child_name": child.get("name"),
            "child_slug": child.get("slug"),
            "relationship": "parent_child",
            "source": child.get("source"),
        })
    relationships.sort(key=lambda row: (row["parent_name"] or "", row["child_name"] or ""))
    output = DATA / "federal_agency_relationships.json"
    output.write_text(json.dumps(relationships, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(output.relative_to(ROOT)), "records": len(relationships)}, indent=2))


if __name__ == "__main__":
    main()
