#!/usr/bin/env python3
"""Fetch compact CDC/ATSDR Social Vulnerability Index 2022 tract data."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
ENDPOINT = "https://onemap.cdc.gov/onemapservices/rest/services/SVI/CDC_ATSDR_Social_Vulnerability_Index_2022_USA/FeatureServer/2/query"
FIELDS = ["ST", "STATE", "ST_ABBR", "STCNTY", "FIPS", "LOCATION", "AREA_SQMI", "E_TOTPOP", "E_HU", "E_HH", "EP_POV150", "EP_UNEMP", "EP_HBURD", "EP_NOHSDP", "EP_UNINSUR", "EP_AGE65", "EP_AGE17", "EP_DISABL", "EP_SNGPNT", "EP_LIMENG", "EP_MINRTY", "EP_MUNIT", "EP_MOBILE", "EP_CROWD", "EP_NOVEH", "EP_GROUPQ", "RPL_THEME1", "RPL_THEME2", "RPL_THEME3", "RPL_THEME4", "RPL_THEMES", "F_TOTAL", "E_NOINT", "EP_NOINT", "E_DAYPOP", "GRASP_ID"]


def main():
    rows, offset = [], 0
    while True:
        query = urlencode({"where": "1=1", "outFields": ",".join(FIELDS), "returnGeometry": "false", "orderByFields": "FIPS", "resultOffset": offset, "resultRecordCount": 2000, "f": "json"})
        payload = json.load(urlopen(ENDPOINT + "?" + query, timeout=180))
        batch = [feature["attributes"] for feature in payload.get("features", [])]
        rows.extend(batch)
        if len(batch) < 2000:
            break
        offset += len(batch)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    for row in rows:
        row["GEOID"] = row.pop("FIPS")
        row["source"] = ENDPOINT
        row["vintage"] = "CDC/ATSDR SVI 2022"
        row["retrieved_at"] = retrieved_at
    rows.sort(key=lambda row: row["GEOID"])
    # Keep each release file comfortably below GitHub's recommended file size.
    parts = [rows[index:index + 22000] for index in range(0, len(rows), 22000)]
    outputs = []
    for index, part in enumerate(parts, start=1):
        output = DATA / f"svi_tracts_2022_part{index}.json"
        output.write_text(json.dumps(part, separators=(",", ":")) + "\n", encoding="utf-8")
        outputs.append(str(output.relative_to(ROOT)))
    print(json.dumps({"files": outputs, "records": len(rows), "source": ENDPOINT}, indent=2))


if __name__ == "__main__":
    main()
