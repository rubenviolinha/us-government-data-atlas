#!/usr/bin/env python3
"""Build a machine-readable coverage report from the release catalog."""

from datetime import datetime, timezone
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def domain(filename):
    stem = Path(filename).name
    for prefix, label in (("acs_", "Census ACS demographics"), ("fec_", "FEC elections"), ("current_", "Current officeholders"), ("federal_", "Federal government"), ("state_", "States and population"), ("county", "Counties"), ("place", "Places"), ("zcta", "ZIP/ZCTA"), ("puma", "PUMAs"), ("cbsa", "Metropolitan areas"), ("school", "Schools")):
        if stem.startswith(prefix):
            return label
    return "Other government reference data"


def main():
    catalog = json.loads((ROOT / "metadata" / "catalog.json").read_text(encoding="utf-8"))
    entries = catalog["entries"]
    groups = Counter(domain(entry["file"]) for entry in entries)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalog_datasets": len(entries),
        "domain_counts": dict(sorted(groups.items())),
        "remaining_gated_inputs": ["USPS licensed exact address and ZIP reference data", "Authenticated Census API access for arbitrary custom queries", "Additional state archival office histories where no stable bulk source is available"],
        "reviewed_but_not_ingested": [],
    }
    output = ROOT / "metadata" / "coverage_report.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(output.relative_to(ROOT)), "datasets": len(entries)}, indent=2))


if __name__ == "__main__":
    main()
