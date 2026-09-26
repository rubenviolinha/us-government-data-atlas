#!/usr/bin/env python3
"""Fetch keyless FBI CDE UCR arrest-count time series."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
BASE = "https://cde.ucr.cjis.gov/LATEST/arrest"


def fetch(level, state=None):
    path = f"{level}/{state}/all" if state else f"{level}/all"
    url = f"{BASE}/{path}?{urlencode({'from': '01-2000', 'to': '12-2024', 'type': 'counts'})}"
    request = Request(url, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=60) as response:
        return url, json.load(response)


def flatten(url, payload, level, state, retrieved_at):
    actuals = payload.get("actuals") or payload.get("offenses", {}).get("actuals") or {}
    rates = payload.get("rates") or payload.get("offenses", {}).get("rates") or {}
    keys = set(actuals) | set(rates)
    arrest_key = next((key for key in keys if key.endswith(" Arrests")), next(iter(keys), None))
    periods = sorted(set(actuals.get(arrest_key, {})) | set(rates.get(arrest_key, {})))
    rows = []
    for period in periods:
        rows.append({
            "level": level,
            "state": state,
            "period": period,
            "arrests": actuals.get(arrest_key, {}).get(period),
            "arrest_rate_per_100k": rates.get(arrest_key, {}).get(period),
            "source": url,
            "vintage": "FBI Crime Data Explorer UCR arrest counts 2000-2024",
            "retrieved_at": retrieved_at,
        })
    return rows


def main():
    states = [row["abbr"] for row in json.loads((ROOT / "data/normalized/states.json").read_text())]
    jobs = [("national", None)] + [("state", state) for state in states]
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    failures = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, *job): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                url, payload = future.result()
                rows.extend(flatten(url, payload, *job, retrieved_at))
            except Exception as exc:
                failures.append({"job": job, "error": str(exc)})
    if failures:
        raise RuntimeError(f"FBI CDE arrest fetch failures: {failures}")
    rows.sort(key=lambda row: (row["level"], row.get("state") or "US", row["period"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    output = NORMALIZED / "fbi_cde_arrests_2000_2024.json"
    output.write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": BASE,
        "source_catalog": "https://cde.ucr.cjis.gov/LATEST/webapp/",
        "format": "FBI CDE JSON normalized to long-form JSON",
        "license": "U.S. government public data",
        "vintage": "FBI Crime Data Explorer UCR arrest counts 2000-2024",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "file": "data/normalized/fbi_cde_arrests_2000_2024.json",
        "coverage": "National and 57 state/territory monthly arrest counts and rates",
        "note": "Public CDE endpoint queried without an API key.",
    }
    (RAW / "fbi_cde_arrests_2000_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
