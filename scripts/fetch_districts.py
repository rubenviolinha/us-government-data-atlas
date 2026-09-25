#!/usr/bin/env python3
"""Extract congressional-district attributes from the Census TIGER archive.

The source archive contains geometry and is intentionally not committed. This
script keeps a compact attribute table plus the exact source URL in the manifest.
"""

from datetime import datetime, timezone
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

URL = "https://www2.census.gov/geo/tiger/TIGER2020/CD/tl_2020_us_cd116.zip"


def parse_dbf(payload: bytes) -> list[dict[str, str]]:
    record_count = int.from_bytes(payload[4:8], "little")
    header_length = int.from_bytes(payload[8:10], "little")
    record_length = int.from_bytes(payload[10:12], "little")
    fields = []
    offset = 32
    while payload[offset] != 0x0D:
        descriptor = payload[offset:offset + 32]
        fields.append((descriptor[:11].split(b"\0", 1)[0].decode("ascii"), descriptor[16]))
        offset += 32
    rows = []
    for index in range(record_count):
        record = payload[header_length + index * record_length:header_length + (index + 1) * record_length]
        values = {}
        cursor = 1
        for name, width in fields:
            values[name] = record[cursor:cursor + width].decode("utf-8", "ignore").strip()
            cursor += width
        rows.append(values)
    return rows


def main() -> None:
    request = Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        archive_payload = response.read()
    with ZipFile(io.BytesIO(archive_payload)) as archive:
        dbf_name = next(name for name in archive.namelist() if name.endswith(".dbf"))
        rows = parse_dbf(archive.read(dbf_name))
    rows = [{key: row[key] for key in ("STATEFP", "CD116FP", "GEOID", "NAMELSAD", "LSAD", "CDSESSN") if key in row} for row in rows]
    (NORMALIZED / "congressional_districts_2020.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": URL,
        "vintage": "2020",
        "records": len(rows),
        "geometry": "Available in source archive; not committed to keep the repository compact",
        "file": "data/normalized/congressional_districts_2020.json"
    }
    (RAW / "district_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
