#!/usr/bin/env python3
"""Fetch the USGS public all-earthquakes past-week feed.

The feed is intentionally a rolling snapshot.  Retrieval metadata is retained
so consumers can identify exactly which USGS window was published.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson"


def main():
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=120) as response:
        feed = json.load(response)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for feature in feed.get("features", []):
        props = feature.get("properties") or {}
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        rows.append({
            "id": feature.get("id"),
            "magnitude": props.get("mag"),
            "place": props.get("place"),
            "event_time": props.get("time"),
            "updated_time": props.get("updated"),
            "status": props.get("status"),
            "tsunami": props.get("tsunami"),
            "significance": props.get("sig"),
            "network": props.get("net"),
            "network_code": props.get("code"),
            "magnitude_type": props.get("magType"),
            "event_type": props.get("type"),
            "felt_reports": props.get("felt"),
            "cdi": props.get("cdi"),
            "mmi": props.get("mmi"),
            "alert": props.get("alert"),
            "station_count": props.get("nst"),
            "distance_to_station": props.get("dmin"),
            "rms": props.get("rms"),
            "gap": props.get("gap"),
            "longitude": coords[0] if len(coords) > 0 else None,
            "latitude": coords[1] if len(coords) > 1 else None,
            "depth_km": coords[2] if len(coords) > 2 else None,
            "event_url": props.get("url"),
            "detail_url": props.get("detail"),
            "source": URL,
            "vintage": "USGS all earthquakes past week rolling feed",
            "feed_generated_at": feed.get("metadata", {}).get("generated"),
            "retrieved_at": retrieved_at,
        })
    rows.sort(key=lambda row: row.get("event_time") or 0, reverse=True)
    out = ROOT / "data" / "normalized" / "usgs_earthquakes_past_week.json"
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://earthquake.usgs.gov/earthquakes/feed/",
        "vintage": "USGS all earthquakes past week rolling feed",
        "retrieved_at": retrieved_at,
        "feed_generated_at": feed.get("metadata", {}).get("generated"),
        "records": len(rows),
        "title": feed.get("metadata", {}).get("title"),
    }
    manifest_path = ROOT / "data" / "raw" / "usgs_earthquakes_past_week_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched {len(rows)} USGS earthquake records")


if __name__ == "__main__":
    main()
