#!/usr/bin/env python3
"""Fetch active USGS stream sites with publicly available instantaneous data."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
URL = "https://waterservices.usgs.gov/nwis/site/"


def parse_rdb(text, state):
    lines = [line for line in text.splitlines() if line and not line.startswith("#")]
    if len(lines) < 3:
        return []
    reader = csv.DictReader(io.StringIO("\n".join([lines[0], *lines[2:]])), delimiter="\t")
    rows = []
    for raw in reader:
        if not raw.get("site_no") or raw["site_no"] == "site_no":
            continue

        def number(key, cast=float):
            value = (raw.get(key) or "").strip()
            if not value or value in {".", "-", "--"}:
                return None
            try:
                return cast(value)
            except ValueError:
                return None

        rows.append({
            "agency_code": raw.get("agency_cd", "").strip(),
            "site_no": raw["site_no"].strip(),
            "station_name": raw.get("station_nm", "").strip(),
            "site_type": raw.get("site_tp_cd", "").strip(),
            "latitude": number("dec_lat_va"),
            "longitude": number("dec_long_va"),
            "altitude": number("alt_va"),
            "huc8": raw.get("huc_cd", "").strip() or None,
            "state_fips": state,
        })
    return rows


def main():
    states = json.loads((NORMALIZED / "states.json").read_text(encoding="utf-8"))
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    state_counts = {}
    for state in states:
        state_fips = state["state_fips"]
        if state_fips == "74":
            state_counts[state_fips] = 0
            continue
        query = urlencode({
            "format": "rdb",
            "stateCd": state_fips,
            "siteStatus": "active",
            "hasDataTypeCd": "iv",
            "siteType": "ST",
        })
        request = Request(URL + "?" + query, headers={"User-Agent": "us-government-data-atlas/1.0"})
        for attempt in range(6):
            try:
                with urlopen(request, timeout=120) as response:
                    text = response.read().decode("utf-8", errors="replace")
                break
            except HTTPError as error:
                if error.code == 404:
                    text = ""
                    break
                if attempt == 5:
                    raise
                sleep(2 ** attempt)
            except URLError:
                if attempt == 5:
                    raise
                sleep(2 ** attempt)
        state_rows = parse_rdb(text, state_fips)
        rows.extend(state_rows)
        state_counts[state_fips] = len(state_rows)
        sleep(0.15)

    for row in rows:
        row["source"] = URL
        row["vintage"] = "USGS active stream sites with instantaneous data"
        row["retrieved_at"] = retrieved_at
    rows.sort(key=lambda row: (row["state_fips"], row["site_no"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    filename = "usgs_active_stream_sites.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source": URL,
        "source_catalog": "https://waterservices.usgs.gov/rest/Site-Service.html",
        "format": "USGS RDB tab-delimited site service normalized to JSON",
        "license": "U.S. government public data",
        "vintage": "USGS active stream sites with instantaneous data",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "states_queried": len(states),
        "state_counts": state_counts,
        "file": "data/normalized/" + filename,
        "note": "Keyless public site registry; active stream sites filtered to sites with instantaneous data availability.",
    }
    (RAW / "usgs_active_stream_sites_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in manifest.items() if key != "state_counts"}, indent=2))


if __name__ == "__main__":
    main()
