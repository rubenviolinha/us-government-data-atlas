#!/usr/bin/env python3
"""Fetch a small, reproducible first data release from official public sources."""

from datetime import datetime, timezone
import json
import csv
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "census_state_population_2024": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/state/totals/NST-EST2024-ALLDATA.csv",
    "senate_1789_present": "https://www.senate.gov/senators/Senators1789toPresent.htm",
}


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def main() -> None:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    manifest = {"retrieved_at": retrieved_at, "files": []}

    population_raw = fetch(SOURCES["census_state_population_2024"])
    (RAW / "census_state_population_2024.csv").write_bytes(population_raw)
    text = population_raw.decode("utf-8-sig")
    normalized = list(csv.DictReader(StringIO(text)))
    normalized = [row for row in normalized if row.get("SUMLEV") == "040"]
    (NORMALIZED / "state_population_2024.json").write_text(
        json.dumps(normalized, indent=2) + "\n", encoding="utf-8"
    )
    manifest["files"].append({"path": "data/raw/census_state_population_2024.csv", "source": SOURCES["census_state_population_2024"], "records": len(normalized)})
    manifest["files"].append({"path": "data/normalized/state_population_2024.json", "source": SOURCES["census_state_population_2024"], "records": len(normalized)})

    try:
        senate_html = fetch(SOURCES["senate_1789_present"])
        (RAW / "senate_1789_present.html").write_bytes(senate_html)
        manifest["files"].append({"path": "data/raw/senate_1789_present.html", "source": SOURCES["senate_1789_present"], "bytes": len(senate_html)})
    except Exception as exc:
        manifest["files"].append({"source": SOURCES["senate_1789_present"], "status": "deferred", "reason": str(exc)})

    (RAW / "retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
