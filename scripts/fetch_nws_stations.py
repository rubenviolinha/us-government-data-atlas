#!/usr/bin/env python3
"""Fetch the public National Weather Service observation-station registry."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://api.weather.gov/stations?limit=500"
HEADERS = {"User-Agent": "us-government-data-atlas/1.0 (public data catalog)"}


def fetch(url):
    with urlopen(Request(url, headers=HEADERS), timeout=120) as response:
        return json.load(response)


def main():
    url = URL
    features = []
    pages = 0
    seen_urls = set()
    seen_feature_ids = set()
    while url:
        if url in seen_urls:
            break
        seen_urls.add(url)
        payload = fetch(url)
        page_features = payload.get("features", [])
        page_ids = {feature.get("id") for feature in page_features if feature.get("id")}
        if page_ids and page_ids.issubset(seen_feature_ids):
            break
        features.extend(page_features)
        seen_feature_ids.update(page_ids)
        pages += 1
        if pages >= 100:
            break
        if pages % 10 == 0:
            print(f"Fetched {len(features)} stations...", flush=True)
        url = payload.get("pagination", {}).get("next")
        if url:
            url = urljoin(URL, url)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for feature in features:
        props = feature.get("properties") or {}
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        elevation = props.get("elevation") or {}
        rows.append({
            "station_id": props.get("stationIdentifier"),
            "name": props.get("name"),
            "latitude": coords[1] if len(coords) > 1 else None,
            "longitude": coords[0] if coords else None,
            "elevation_m": elevation.get("value"),
            "elevation_unit": elevation.get("unitCode"),
            "time_zone": props.get("timeZone"),
            "provider": props.get("provider"),
            "sub_provider": props.get("subProvider"),
            "forecast_zone_url": props.get("forecast"),
            "county_zone_url": props.get("county"),
            "fire_weather_zone_url": props.get("fireWeatherZone"),
            "station_url": feature.get("id") or props.get("@id"),
            "source": "https://api.weather.gov/stations",
            "vintage": "NWS public observation-station registry",
            "retrieved_at": retrieved_at,
        })
    unique_rows = {row.get("station_id"): row for row in rows if row.get("station_id")}
    rows = sorted(unique_rows.values(), key=lambda row: row.get("station_id") or "")
    out = ROOT / "data" / "normalized" / "nws_stations.json"
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": "https://api.weather.gov/stations",
        "source_catalog": "https://www.weather.gov/documentation/services-web-api",
        "vintage": "NWS public observation-station registry",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "pages": pages,
    }
    manifest_path = ROOT / "data" / "raw" / "nws_stations_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched {len(rows)} NWS observation stations across {pages} pages")


if __name__ == "__main__":
    main()
