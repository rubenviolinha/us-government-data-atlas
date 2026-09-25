#!/usr/bin/env python3
"""Build an as-of-today view of federal judges with an active appointment."""

from datetime import date
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"


def main():
    as_of = date.today().isoformat()
    historical = json.loads((DATA / "federal_judges.json").read_text(encoding="utf-8"))
    current = []
    for row in historical:
        appointments = []
        for index in range(1, 7):
            court = row.get(f"Court Name ({index})", "").strip()
            commission = row.get(f"Commission Date ({index})", "").strip()
            termination = row.get(f"Termination Date ({index})", "").strip()
            if not court or not commission or commission > as_of or (termination and termination < as_of):
                continue
            appointments.append({
                "court": court,
                "court_type": row.get(f"Court Type ({index})", "").strip(),
                "title": row.get(f"Appointment Title ({index})", "").strip(),
                "seat_id": row.get(f"Seat ID ({index})", "").strip(),
                "commission_date": commission,
                "senior_status_date": row.get(f"Senior Status Date ({index})", "").strip() or None,
                "termination_date": termination or None,
            })
        if appointments:
            current.append({**row, "active_appointments": appointments, "view_as_of": as_of, "view_type": "currently_serving"})
    current.sort(key=lambda row: (row.get("Last Name", ""), row.get("First Name", ""), row.get("jid", "")))
    output = DATA / "current_federal_judges.json"
    output.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(output.relative_to(ROOT)), "records": len(current), "view_as_of": as_of}, indent=2))


if __name__ == "__main__":
    main()
