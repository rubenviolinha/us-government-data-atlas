#!/usr/bin/env python3
"""Fetch the National Governors Association current-governor roster."""

from datetime import datetime, timezone
import json, re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
URL = "https://www.nga.org/governors/"


def main():
    html = urlopen(Request(URL, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=120).read().decode("utf-8", "ignore")
    blocks = re.findall(r'<li class="current-governors__item.*?</li>', html, re.S)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for block in blocks:
        state = re.search(r'<small class="state">\s*([^<]+?)\s*</small>', block, re.S)
        name = re.search(r'Gov\.\s*([^<]+?)\s*</div>', block, re.S)
        profile = re.search(r'href\s*=\s*"([^"]+)"', block, re.S)
        if state and name:
            rows.append({"state": state.group(1).strip(), "name": name.group(1).strip(), "profile_url": profile.group(1) if profile else URL, "source": URL, "retrieved_at": retrieved_at})
    rows.sort(key=lambda row: row["state"])
    DATA.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    filename = "current_governors_nga.json"
    (DATA / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": retrieved_at, "source": URL, "format": "NGA HTML roster", "records": len(rows), "file": "data/normalized/" + filename, "note": "Current state and territory governors from the NGA roster; no API key used."}
    (RAW / "current_governors_nga_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
