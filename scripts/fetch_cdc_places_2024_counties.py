#!/usr/bin/env python3
"""Fetch CDC PLACES 2024 county health indicators without an API key.

The public Socrata endpoint is paginated and the normalized release is split
into repository-safe parts. Values remain long-form: one row per county,
measure, and estimate type, with the CDC's confidence limits preserved.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
ENDPOINT = "https://data.cdc.gov/resource/fu4u-a9bh.json"
FIELDS = (
    "year,stateabbr,statedesc,locationname,category,measure,data_value_unit,"
    "data_value_type,data_value,low_confidence_limit,high_confidence_limit,"
    "totalpopulation,totalpop18plus,locationid,categoryid,measureid,"
    "datavaluetypeid"
)
PAGE_SIZE = 50000
PART_SIZE = 60000


def fetch_page(offset):
    query = urlencode({
        "$select": FIELDS,
        "$order": "locationid,measureid,datavaluetypeid",
        "$limit": PAGE_SIZE,
        "$offset": offset,
    })
    url = ENDPOINT + "?" + query
    with urlopen(Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=180) as response:
        return url, json.loads(response.read().decode("utf-8"))


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    offset = 0
    source_urls = []
    while True:
        url, page = fetch_page(offset)
        source_urls.append(url)
        if not page:
            break
        for row in page:
            row["source"] = ENDPOINT
            row["vintage"] = "CDC PLACES 2024 release (estimates for 2022)"
            row["retrieved_at"] = retrieved_at
        rows.extend(page)
        offset += len(page)
        if len(page) < PAGE_SIZE:
            break

    assert len(rows) >= 240000, len(rows)
    assert len({row.get("locationid") for row in rows}) >= 3100
    assert all(row.get("measureid") and row.get("data_value_type") for row in rows)
    outputs = {}
    for index, start in enumerate(range(0, len(rows), PART_SIZE), start=1):
        part = rows[start:start + PART_SIZE]
        filename = f"cdc_places_counties_2024_part{index}.json"
        (NORMALIZED / filename).write_text(json.dumps(part, separators=(",", ":")) + "\n", encoding="utf-8")
        outputs[filename] = {"file": "data/normalized/" + filename, "records": len(part), "source": ENDPOINT}

    manifest = {
        "retrieved_at": retrieved_at,
        "dataset": "CDC PLACES: Local Data for Better Health, County Data 2024 release",
        "source": ENDPOINT,
        "source_page": "https://data.cdc.gov/d/fu4u-a9bh",
        "records": len(rows),
        "county_locations": len({row["locationid"] for row in rows}),
        "parts": outputs,
        "note": "Public CDC Socrata data; no API key used. Values are model-based local estimates and are preserved in long form with confidence limits.",
    }
    (RAW / "cdc_places_counties_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
