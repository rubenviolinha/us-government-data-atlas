#!/usr/bin/env python3
"""Fetch keyless ACS 5-year profile variable metadata for core demographic groups."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "acs-profile-groups"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

BASE = "https://api.census.gov/data/2023/acs/acs5/profile/groups/"
GROUPS = ["DP02", "DP03", "DP04", "DP05"]


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    variables = []
    for group in GROUPS:
        url = BASE + group + ".json"
        request = Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"})
        with urlopen(request, timeout=120) as response:
            payload = response.read()
        (RAW / f"{group}.json").write_bytes(payload)
        document = json.loads(payload)
        for name, variable in document.get("variables", {}).items():
            variables.append({
                "name": name,
                "label": variable.get("label"),
                "concept": variable.get("concept"),
                "predicate_type": variable.get("predicateType"),
                "group": variable.get("group", group),
                "limit": variable.get("limit"),
                "predicate_only": variable.get("predicateOnly", False),
                "attributes": variable.get("attributes"),
                "source": url,
            })
    variables.sort(key=lambda row: row["name"])
    output = NORMALIZED / "acs_profile_variables_2023.json"
    output.write_text(json.dumps(variables, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "sources": [BASE + group + ".json" for group in GROUPS],
        "raw_directory": "data/raw/acs-profile-groups",
        "file": "data/normalized/acs_profile_variables_2023.json",
        "groups": GROUPS,
        "variables": len(variables),
        "note": "Variable metadata is keyless; ACS value queries may require an API key in this environment.",
    }
    (RAW.parent / "acs_profile_metadata_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
