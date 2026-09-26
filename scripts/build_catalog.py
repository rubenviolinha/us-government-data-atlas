#!/usr/bin/env python3
"""Build a machine-readable catalog of normalized release files."""

from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
OUTPUT = ROOT / "metadata" / "catalog.json"


def main():
    entries = []
    paths = sorted(DATA.glob("*.json"))
    for index, path in enumerate(paths, 1):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else []
        fields = sorted({field for row in rows[:100] if isinstance(row, dict) for field in row})
        sources = sorted({row.get("source") for row in rows[:100] if isinstance(row, dict) and row.get("source")})
        entries.append({
            "file": "data/normalized/" + path.name,
            "format": "JSON",
            "records": len(rows),
            "size_bytes": path.stat().st_size,
            "fields_sample": fields,
            "source_urls_sample": sources,
        })
        if index % 25 == 0:
            print(f"catalogued {index}/{len(paths)} files", flush=True)
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": "Machine-readable inventory of normalized US Government Data Atlas releases.",
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalog": str(OUTPUT.relative_to(ROOT)), "datasets": len(entries)}, indent=2))


if __name__ == "__main__":
    main()
