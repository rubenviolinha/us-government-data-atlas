#!/usr/bin/env python3
"""Build an as-of-today view of currently serving Supreme Court justices."""

from datetime import date
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"


def main():
    as_of = date.today().isoformat()
    historical = json.loads((DATA / "supreme_court_justices.json").read_text(encoding="utf-8"))
    current = []
    for row in historical:
        oath_date = row.get("oath_date")
        ended = row.get("service_terminated_date")
        if not oath_date or oath_date > as_of or (ended and ended < as_of):
            continue
        current.append({**row, "view_as_of": as_of, "view_type": "currently_serving"})
    current.sort(key=lambda row: (row["role"] != "chief", row["oath_date"], row["name"]))
    output = DATA / "current_supreme_court_justices.json"
    output.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(output.relative_to(ROOT)), "records": len(current), "view_as_of": as_of}, indent=2))


if __name__ == "__main__":
    main()
