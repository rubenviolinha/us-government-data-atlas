#!/usr/bin/env python3
"""Fetch the public USDOT/BTS aviation-facilities layer."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
ENDPOINT = "https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_Aviation_Facilities/FeatureServer/0/query"
SOURCE = "https://data.bts.gov/"
FIELDS = [
    "EFF_DATE", "SITE_NO", "SITE_TYPE_CODE", "STATE_CODE", "ARPT_ID", "CITY",
    "COUNTRY_CODE", "REGION_CODE", "STATE_NAME", "COUNTY_NAME", "ARPT_NAME",
    "OWNERSHIP_TYPE_CODE", "FACILITY_USE_CODE", "LAT_DECIMAL", "LONG_DECIMAL",
    "ELEV", "TPA", "DIST_CITY_TO_AIRPORT", "DIRECTION_CODE", "ACREAGE",
    "ARTCC_NAME", "PHONE_NO", "TOLL_FREE_NO", "NOTAM_ID", "ARPT_STATUS",
    "FAR_139_TYPE_CODE", "JOINT_USE_FLAG", "LNDG_RIGHTS_FLAG", "ACTIVATION_DATE",
]


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    rows, offset = [], 0
    while True:
        query = urlencode({
            "where": "1=1", "outFields": ",".join(FIELDS), "returnGeometry": "false",
            "orderByFields": "SITE_NO", "resultOffset": offset, "resultRecordCount": 2000, "f": "json",
        })
        payload = json.load(urlopen(ENDPOINT + "?" + query, timeout=120))
        batch = [feature["attributes"] for feature in payload.get("features", [])]
        rows.extend(batch)
        print(f"Fetched {len(rows)} aviation facilities", flush=True)
        if len(batch) < 2000:
            break
        offset += len(batch)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    for row in rows:
        row = row
        for field in list(row):
            row[field.lower()] = row.pop(field)
        row["source"] = ENDPOINT
        row["source_catalog"] = SOURCE
        row["vintage"] = "FAA-updated USDOT/BTS Aviation Facilities"
        row["retrieved_at"] = retrieved_at
    rows.sort(key=lambda row: row.get("site_no") or "")
    filename = "bts_aviation_facilities.json"
    (DATA / filename).write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": SOURCE, "endpoint": ENDPOINT, "records": len(rows), "file": "data/normalized/" + filename, "note": "FAA-updated USDOT/BTS Aviation Facilities layer; no API key used."}
    (RAW / "bts_aviation_facilities_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
