#!/usr/bin/env python3
"""Build the small, dependency-free GitHub Pages site for the Atlas API."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CATALOG_PATH = ROOT / "metadata" / "catalog.json"
SOURCES_PATH = ROOT / "metadata" / "sources.json"


def build_summary() -> dict:
    catalog = json.loads(CATALOG_PATH.read_text())
    entries = catalog["entries"]
    groups: dict[str, int] = {}
    for entry in entries:
        name = Path(entry["file"]).stem
        group = re.sub(r"_part\d+$", "", name)
        groups[group] = groups.get(group, 0) + 1
    total_records = sum(entry.get("records", 0) for entry in entries)
    largest = sorted(entries, key=lambda item: item.get("records", 0), reverse=True)[:8]
    sources = json.loads(SOURCES_PATH.read_text())
    source_entries = sources.get("sources", []) if isinstance(sources, dict) else sources
    return {
        "generated_at": catalog.get("generated_at"),
        "dataset_file_count": len(entries),
        "logical_group_count": len(groups),
        "total_records": total_records,
        "source_count": len(source_entries),
        "largest_datasets": [
            {"file": item["file"], "records": item.get("records", 0)} for item in largest
        ],
    }


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    summary = build_summary()
    (DOCS / "catalog-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        f"Wrote docs/catalog-summary.json: {summary['dataset_file_count']} files, "
        f"{summary['logical_group_count']} logical groups"
    )


if __name__ == "__main__":
    main()
