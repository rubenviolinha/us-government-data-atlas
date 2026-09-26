#!/usr/bin/env python3
"""Fetch the public FBI Crime Data Explorer agency/ORI registry."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
BASE = "https://cde.ucr.cjis.gov/LATEST/agency/byStateAbbr/"


def fetch(state):
    url = BASE + state
    request = Request(url, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=60) as response:
        return url, json.load(response)


def main():
    states = [row["abbr"] for row in json.loads((ROOT / "data/normalized/states.json").read_text())]
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    failures = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, state): state for state in states}
        for future in as_completed(futures):
            state = futures[future]
            try:
                url, payload = future.result()
                for county, agencies in payload.items():
                    if not isinstance(agencies, list):
                        continue
                    for agency in agencies:
                        row = dict(agency)
                        row["county_group"] = county
                        row["source"] = url
                        row["vintage"] = "FBI Crime Data Explorer agency registry retrieved 2026-09-26"
                        row["retrieved_at"] = retrieved_at
                        rows.append(row)
            except Exception as exc:
                failures.append({"state": state, "error": str(exc)})
    if failures:
        raise RuntimeError(f"FBI CDE agency fetch failures: {failures}")
    rows.sort(key=lambda row: row.get("ori") or "")
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    output = NORMALIZED / "fbi_cde_agencies_2026.json"
    output.write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": BASE,
        "source_catalog": "https://cde.ucr.cjis.gov/LATEST/webapp/",
        "format": "FBI CDE JSON normalized to JSON",
        "license": "U.S. government public data",
        "vintage": "FBI Crime Data Explorer agency registry retrieved 2026-09-26",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "file": "data/normalized/fbi_cde_agencies_2026.json",
        "coverage": "Agency ORI records returned for the 57 states and territories in the repository state registry",
        "note": "Includes agency names, types, county groups, coordinates, NIBRS participation, and NIBRS start dates; no API key used.",
    }
    (RAW / "fbi_cde_agencies_2026_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
