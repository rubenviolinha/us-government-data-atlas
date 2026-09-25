#!/usr/bin/env python3
"""Fetch the compact GNIS government-units extract without an API key."""

from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/Topical/GovernmentUnits_National_Text.zip"
POPULATED_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/Topical/PopulatedPlaces_National_Text.zip"


def main() -> None:
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    (RAW / "gnis_government_units_national.zip").write_bytes(payload)
    with ZipFile(io.BytesIO(payload)) as archive:
        text_name = next(name for name in archive.namelist() if name.endswith(".txt"))
        text = archive.read(text_name).decode("utf-8-sig")
    rows = [{key.strip(): value.strip() for key, value in row.items()} for row in csv.DictReader(io.StringIO(text), delimiter="|")]
    (NORMALIZED / "gnis_government_units.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": URL,
        "records": len(rows),
        "unit_types": sorted({row.get("unit_type") for row in rows}),
        "files": ["data/raw/gnis_government_units_national.zip", "data/normalized/gnis_government_units.json"]
    }
    (RAW / "gnis_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    pop_request = Request(POPULATED_URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(pop_request, timeout=60) as response:
        populated_payload = response.read()
    (RAW / "gnis_populated_places_national.zip").write_bytes(populated_payload)
    with ZipFile(io.BytesIO(populated_payload)) as archive:
        populated_name = next(name for name in archive.namelist() if name.endswith(".txt"))
        populated_text = archive.read(populated_name).decode("utf-8-sig")
    populated = [{key.strip(): value.strip() for key, value in row.items()} for row in csv.DictReader(io.StringIO(populated_text), delimiter="|")]
    (NORMALIZED / "gnis_populated_places.json").write_text(json.dumps(populated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest["populated_places"] = {"source": POPULATED_URL, "records": len(populated), "file": "data/normalized/gnis_populated_places.json"}
    (RAW / "gnis_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
