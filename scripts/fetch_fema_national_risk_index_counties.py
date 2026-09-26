#!/usr/bin/env python3
"""Fetch FEMA National Risk Index county records from the public ArcGIS service."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
SERVICE = "https://services.arcgis.com/HdtZMT2FmI4wPzTM/ArcGIS/rest/services/FEMA_National_Risk_Index/FeatureServer/0"
QUERY = SERVICE + "/query"
OUTPUT = NORMALIZED / "fema_national_risk_index_counties.json"


def main():
    schema_request = Request(SERVICE + "?f=json", headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(schema_request, timeout=60) as response:
        schema = json.load(response)
    names = [field["name"] for field in schema["fields"]]
    core = ["NRI_ID", "STATE", "STATEABBRV", "STATEFIPS", "COUNTY", "COUNTYTYPE", "COUNTYFIPS", "STCOFIPS", "POPULATION", "AREA", "RISK_VALUE", "RISK_SCORE", "RISK_RATNG", "EAL_SCORE", "EAL_RATNG", "EAL_VALT", "SOVI_SCORE", "SOVI_RATNG", "RESL_SCORE", "RESL_RATNG", "NRI_VER"]
    hazard_scores = [name for name in names if name.endswith("_RISKS")]
    fields = core + hazard_scores
    rows = []
    for offset in range(0, 10000, 1000):
        params = {"where": "1=1", "outFields": ",".join(fields), "returnGeometry": "false", "resultRecordCount": "1000", "resultOffset": str(offset), "f": "json"}
        request = Request(QUERY + "?" + urlencode(params), headers={"User-Agent": "us-government-data-atlas/1.0"})
        with urlopen(request, timeout=120) as response:
            payload = json.load(response)
        rows.extend(feature["attributes"] for feature in payload.get("features", []))
        if not payload.get("exceededTransferLimit"):
            break
    retrieved_at = datetime.now(timezone.utc).isoformat()
    normalized = []
    for raw in rows:
        row = {key.lower(): value for key, value in raw.items()}
        row.update({"source": QUERY, "vintage": f"FEMA National Risk Index {raw.get('NRI_VER') or 'public service'}", "retrieved_at": retrieved_at})
        normalized.append(row)
    normalized.sort(key=lambda row: row.get("stcofips") or "")
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(normalized, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": QUERY,
        "source_catalog": "https://www.fema.gov/flood-maps/products-tools/national-risk-index",
        "format": "Public FEMA ArcGIS FeatureServer JSON normalized to JSON",
        "license": "U.S. government public data",
        "vintage": normalized[0]["vintage"] if normalized else "FEMA National Risk Index public service",
        "retrieved_at": retrieved_at,
        "records": len(normalized),
        "fields": len(fields),
        "file": f"data/normalized/{OUTPUT.name}",
        "note": "County-level composite risk, expected annual loss, social vulnerability, community resilience, and hazard risk scores; no API key used.",
    }
    (RAW / "fema_national_risk_index_counties_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
