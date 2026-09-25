#!/usr/bin/env python3
"""Fetch keyless state-level ACS age/sex estimates from a table-based summary file."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
NORMALIZED.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

SOURCE_URL = "https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/acsdt5y2023-b01001.dat"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    names = {row["state_fips"]: row["name"] for row in json.loads((NORMALIZED / "states.json").read_text())}
    request = Request(SOURCE_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=300) as response:
        header = response.readline().decode("utf-8").rstrip("\n").split("|")
        rows = []
        for line in response:
            if not line.startswith(b"0400000US"):
                continue
            values = next(csv.reader([line.decode("utf-8").rstrip("\n")], delimiter="|"))
            row = dict(zip(header, values))
            fips = row["GEO_ID"][-2:]
            row = {key: (int(value) if value.lstrip("-").isdigit() else value) for key, value in row.items()}
            row["state_fips"] = fips
            row["state_name"] = names.get(fips)
            row["source"] = SOURCE_URL
            rows.append(row)
    rows.sort(key=lambda row: row["GEO_ID"])
    output = NORMALIZED / "acs_state_age_sex_2023.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": SOURCE_URL,
        "file": "data/normalized/acs_state_age_sex_2023.json",
        "records": len(rows),
        "table": "B01001",
        "geography": "state-level 0400000US records",
        "note": "Downloaded from the public table-based ACS summary file; this fallback does not use the ACS API key."
    }
    (RAW / "acs_state_age_sex_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
