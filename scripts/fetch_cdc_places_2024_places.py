#!/usr/bin/env python3
"""Fetch the public CDC PLACES 2024 place release without an API key."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
ENDPOINT = "https://data.cdc.gov/resource/sd8v-uq83.json"
FIELDS = (
    "year,stateabbr,statedesc,locationname,datasource,category,measure,data_value_unit,"
    "data_value_type,data_value,low_confidence_limit,high_confidence_limit,"
    "totalpopulation,totalpop18plus,locationid,categoryid,measureid,datavaluetypeid,short_question_text"
)
PAGE_SIZE = 50000
PART_SIZE = 60000


def fetch_page(offset):
    query = urlencode({"$select": FIELDS, "$order": "locationid,measureid,datavaluetypeid", "$limit": PAGE_SIZE, "$offset": offset})
    url = ENDPOINT + "?" + query
    with urlopen(Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=240) as response:
        return url, json.loads(response.read().decode("utf-8"))


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows, offset = [], 0
    while True:
        _url, page = fetch_page(offset)
        if not page:
            break
        for row in page:
            row.update({"source": ENDPOINT, "vintage": "CDC PLACES 2024 release (estimates for 2022)", "retrieved_at": retrieved_at})
        rows.extend(page)
        offset += len(page)
        if len(page) < PAGE_SIZE:
            break
    assert len(rows) >= 2200000, len(rows)
    assert len({row.get("locationid") for row in rows}) >= 29000
    assert all(row.get("measureid") and row.get("data_value_type") for row in rows)

    parts = {}
    for index, start in enumerate(range(0, len(rows), PART_SIZE), start=1):
        part = rows[start:start + PART_SIZE]
        filename = f"cdc_places_named_places_2024_part{index}.json"
        (NORMALIZED / filename).write_text(json.dumps(part, separators=(",", ":")) + "\n", encoding="utf-8")
        parts[filename] = {"file": "data/normalized/" + filename, "records": len(part), "source": ENDPOINT}

    manifest = {"retrieved_at": retrieved_at, "dataset": "CDC PLACES: Local Data for Better Health, Place Data 2024 release", "source": ENDPOINT, "source_page": "https://data.cdc.gov/d/sd8v-uq83", "records": len(rows), "place_locations": len({row["locationid"] for row in rows}), "parts": parts, "note": "Public CDC Socrata data; no API key used. Values are model-based local estimates and are preserved in long form with confidence limits."}
    (RAW / "cdc_places_named_places_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
