#!/usr/bin/env python3
"""Fetch compact nationwide CDC/ATSDR SVI 2022 ZCTA data."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
ENDPOINT = "https://onemap.cdc.gov/OneMapServices/rest/services/SVI/SVI_consolidated_data/FeatureServer/0/query"
FIELDS = ["GRASPID", "ST", "FIPS", "E_TOTPOP", "E_HU", "E_HH", "Overall_SVI_Percentile", "Theme1_Percentile", "Theme2_Percentile", "Theme3_Percentile", "Theme4_Percentile", "Theme1_EPL_POV", "Theme1_EPL_UNEMP", "Theme1_EPL_HBURD", "Theme1_EPL_NOHSDP", "Theme1_EPL_UNINSUR", "Theme2_EPL_AGE65", "Theme2_EPL_AGE17", "Theme2_EPL_DISABL", "Theme2_EPL_SNGPNT", "Theme2_EPL_LIMENG", "Theme3_EPL_MINRTY", "Theme4_EPL_MUNIT", "Theme4_EPL_MOBILE", "Theme4_EPL_CROWD", "Theme4_EPL_NOVEH", "Theme4_EPL_GROUPQ", "F_POV150", "F_HBURD", "F_UNINSUR", "E_NOINT", "EP_NOINT", "E_HISP", "EP_HISP"]


def main():
    rows, offset = [], 0
    while True:
        query = urlencode({"where": "GeoLevel='zcta' AND ReleaseYear=2022 AND Comparison='national'", "outFields": ",".join(FIELDS), "returnGeometry": "false", "orderByFields": "FIPS", "resultOffset": offset, "resultRecordCount": 2000, "f": "json"})
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
        row["comparison"] = "national"
        row["retrieved_at"] = retrieved_at
    rows.sort(key=lambda row: row["GEOID"])
    output = DATA / "svi_zctas_2022.json"
    output.write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(output.relative_to(ROOT)), "records": len(rows), "source": ENDPOINT}, indent=2))


if __name__ == "__main__":
    main()
