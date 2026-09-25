#!/usr/bin/env python3
"""Fetch current and retired state legislators from Open States' public bulk repo."""

from datetime import date, datetime, timezone
import io
import json
from pathlib import Path
import tarfile
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
ARCHIVE = "https://codeload.github.com/openstates/people/tar.gz/refs/heads/main"
SOURCE = "https://github.com/openstates/people"


def normalize(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    request = Request(ARCHIVE, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=300) as response:
        payload = response.read()
    records = []
    counts = {"current": 0, "retired": 0}
    excluded_federal_records = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        for member in archive.getmembers():
            parts = member.name.split("/")
            if len(parts) != 5 or parts[1] != "data" or parts[3] not in {"legislature", "retired"} or not parts[4].endswith(".yml"):
                continue
            state = parts[2]
            if state == "us":
                excluded_federal_records += 1
                continue
            record_type = "current" if parts[3] == "legislature" else "retired"
            handle = archive.extractfile(member)
            if handle is None:
                continue
            record = normalize(yaml.safe_load(handle.read()) or {})
            record.update({"state": state.upper(), "record_type": record_type, "source": SOURCE})
            records.append(record)
            counts[record_type] += 1
    records.sort(key=lambda row: (row["state"], row.get("name", ""), row.get("id", "")))
    output = NORMALIZED / "state_legislators_openstates.json"
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE,
        "archive": ARCHIVE,
        "records": len(records),
        "excluded_federal_records": excluded_federal_records,
        "current_records": counts["current"],
        "retired_records": counts["retired"],
        "license_note": "Open States states that its bulk data is provided under a public-domain dedication; verify attribution and source terms before redistribution.",
        "file": "data/normalized/state_legislators_openstates.json",
    }
    (RAW / "state_legislators_openstates_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
