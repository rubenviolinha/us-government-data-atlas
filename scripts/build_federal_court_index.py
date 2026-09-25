#!/usr/bin/env python3
"""Build a compact index of federal courts represented in the FJC roster."""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
SOURCE = "https://www.fjc.gov/history/judges"


def main():
    historical = json.loads((DATA / "federal_judges.json").read_text(encoding="utf-8"))
    current = json.loads((DATA / "current_federal_judges.json").read_text(encoding="utf-8"))
    totals = defaultdict(lambda: {"court_type": "", "historical_judge_records": 0, "current_judge_records": 0, "active_appointments": 0})
    for row in historical:
        seen = set()
        for index in range(1, 7):
            court = (row.get(f"Court Name ({index})") or "").strip()
            if not court:
                continue
            entry = totals[court]
            entry["court_type"] = entry["court_type"] or (row.get(f"Court Type ({index})") or "").strip()
            if court not in seen:
                entry["historical_judge_records"] += 1
                seen.add(court)
    for row in current:
        seen = set()
        for appointment in row.get("active_appointments", []):
            court = appointment.get("court", "").strip()
            if not court:
                continue
            entry = totals[court]
            entry["court_type"] = entry["court_type"] or appointment.get("court_type", "").strip()
            entry["active_appointments"] += 1
            if court not in seen:
                entry["current_judge_records"] += 1
                seen.add(court)
    as_of = current[0]["view_as_of"] if current else None
    rows = []
    for court in sorted(totals):
        rows.append({"court_name": court, **totals[court], "view_as_of": as_of, "source": SOURCE})
    output = DATA / "federal_court_index.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(output.relative_to(ROOT)), "records": len(rows), "view_as_of": as_of}, indent=2))


if __name__ == "__main__":
    main()
