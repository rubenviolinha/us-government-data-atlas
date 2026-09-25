#!/usr/bin/env python3
"""Build a content-addressed manifest for the normalized release."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
OUTPUT = ROOT / "metadata" / "release_manifest.json"


def main():
    entries = []
    for path in sorted(DATA.glob("*.json")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append({
            "file": "data/normalized/" + path.name,
            "sha256": digest,
            "size_bytes": path.stat().st_size,
        })
    manifest = {
        "release_id": datetime.now(timezone.utc).strftime("%Y%m%d"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "sha256",
        "dataset_count": len(entries),
        "datasets": entries,
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(OUTPUT.relative_to(ROOT)), "datasets": len(entries)}, indent=2))


if __name__ == "__main__":
    main()
