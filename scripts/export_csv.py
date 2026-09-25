#!/usr/bin/env python3
"""Export one catalog-listed normalized JSON dataset as CSV."""

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
CATALOG = ROOT / "metadata" / "catalog.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", help="JSON filename from data/normalized")
    parser.add_argument("output", help="CSV output path")
    args = parser.parse_args()
    allowed = {entry["file"].removeprefix("data/normalized/") for entry in json.loads(CATALOG.read_text())["entries"]}
    if args.dataset not in allowed:
        parser.error("dataset is not listed in metadata/catalog.json")
    payload = json.loads((DATA / args.dataset).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
        parser.error("dataset must contain a list of objects")
    fields = sorted({field for row in payload for field in row})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in payload:
            writer.writerow({field: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value for field, value in row.items()})
    print(json.dumps({"dataset": args.dataset, "output": str(output), "records": len(payload), "fields": len(fields)}, indent=2))


if __name__ == "__main__":
    main()
