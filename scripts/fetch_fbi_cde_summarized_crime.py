#!/usr/bin/env python3
"""Fetch keyless FBI Crime Data Explorer summarized UCR crime series."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
BASE = "https://cde.ucr.cjis.gov/LATEST/summarized"
FROM = "01-2000"
TO = "12-2024"
GROUPS = {"V": "violent_crime", "P": "property_crime"}


def fetch(level, group, state=None):
    subject = f"{level}/{state}/{group}" if state else f"{level}/{group}"
    query = urlencode({"from": FROM, "to": TO, "type": "counts"})
    url = f"{BASE}/{subject}?{query}"
    request = Request(url, headers={"User-Agent": "us-government-data-atlas/1.0"})
    with urlopen(request, timeout=60) as response:
        return url, json.load(response)


def flatten(url, payload, level, group, state=None, retrieved_at=None):
    offenses = payload.get("offenses", {})
    actuals = offenses.get("actuals") or {}
    rates = offenses.get("rates") or {}
    keys = set(actuals) | set(rates)
    offense_key = next((key for key in keys if key.endswith(" Offenses")), None)
    clearance_key = next((key for key in keys if key.endswith(" Clearances")), None)
    populations = payload.get("populations", {})
    population_map = next(iter(populations.get("population", {}).values()), {})
    participated_map = next(iter(populations.get("participated_population", {}).values()), {})
    periods = sorted(set(actuals.get(offense_key, {})) | set(rates.get(offense_key, {})))
    rows = []
    for period in periods:
        rows.append({
            "level": level,
            "state": state,
            "crime_group": GROUPS[group],
            "period": period,
            "offenses": actuals.get(offense_key, {}).get(period),
            "offense_rate_per_100k": rates.get(offense_key, {}).get(period),
            "clearances": actuals.get(clearance_key, {}).get(period) if clearance_key else None,
            "clearance_rate_per_100k": rates.get(clearance_key, {}).get(period) if clearance_key else None,
            "population": population_map.get(period),
            "participated_population": participated_map.get(period),
            "source": url,
            "vintage": "FBI Crime Data Explorer summarized UCR 2000-2024",
            "retrieved_at": retrieved_at,
        })
    return rows


def main():
    states = [row["abbr"] for row in json.loads((ROOT / "data/normalized/states.json").read_text())]
    jobs = [("national", group, None) for group in GROUPS]
    jobs += [("state", group, state) for state in states for group in GROUPS]
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    failures = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, *job): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                url, payload = future.result()
                rows.extend(flatten(url, payload, *job, retrieved_at=retrieved_at))
            except Exception as exc:
                failures.append({"job": job, "error": str(exc)})
    if failures:
        raise RuntimeError(f"FBI CDE fetch failures: {failures}")
    rows.sort(key=lambda row: (row["level"], row.get("state") or "US", row["crime_group"], row["period"]))
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    output = NORMALIZED / "fbi_cde_summarized_crime_2000_2024.json"
    output.write_text(json.dumps(rows, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {
        "source": BASE,
        "source_catalog": "https://cde.ucr.cjis.gov/LATEST/webapp/",
        "format": "FBI CDE JSON normalized to long-form JSON",
        "license": "U.S. government public data",
        "vintage": "FBI Crime Data Explorer summarized UCR 2000-2024",
        "retrieved_at": retrieved_at,
        "records": len(rows),
        "file": "data/normalized/fbi_cde_summarized_crime_2000_2024.json",
        "coverage": "National and 57 states/territories; monthly 2000-2024 violent and property crime summaries",
        "note": "Public CDE host was queried without an API key; values reflect FBI summarized UCR series and participation populations.",
    }
    (RAW / "fbi_cde_summarized_crime_2000_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
