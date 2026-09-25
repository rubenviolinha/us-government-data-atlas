#!/usr/bin/env python3
"""Fetch the State Department Historian's alphabetical principal-officer index."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "state-department-principals"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

BASE = "https://history.state.gov/departmenthistory/people/by-name/"


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    people = {}
    pages = []
    for letter in "abcdefghijklmnopqrstuvwxyz":
        url = BASE + letter
        request = Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"})
        try:
            with urlopen(request, timeout=120) as response:
                payload = response.read()
        except HTTPError as error:
            if error.code == 400:
                continue
            raise
        (RAW / f"{letter}.html").write_bytes(payload)
        pages.append(url)
        soup = BeautifulSoup(payload, "html.parser")
        for link in soup.select("a[href^='/departmenthistory/people/']"):
            if link.find_parent("li") is None:
                continue
            li = link.find_parent("li")
            text = " ".join(link.get_text(" ", strip=True).split())
            dates = re.search(r"\((\d{4})(?:\s*[–-]\s*(\d{4}))?\)$", text)
            name = re.sub(r"\s*\(\d{4}(?:\s*[–-]\s*\d{4})?\)$", "", text).strip()
            roles = [" ".join(item.get_text(" ", strip=True).split()) for item in li.find_all("li", recursive=False)]
            key = link["href"]
            people[key] = {
                "name": name,
                "birth_year": int(dates.group(1)) if dates else None,
                "death_year": int(dates.group(2)) if dates and dates.group(2) else None,
                "roles": roles,
                "profile_url": "https://history.state.gov" + key,
                "source": url,
            }
    rows = sorted(people.values(), key=lambda row: (row["name"], row["profile_url"]))
    if len(rows) < 1000:
        raise RuntimeError(f"Unexpectedly low State Department principal-officer count: {len(rows)}")
    output = NORMALIZED / "state_department_principals.json"
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": BASE,
        "raw_directory": "data/raw/state-department-principals",
        "file": "data/normalized/state_department_principals.json",
        "records": len(rows),
        "pages": len(pages),
        "scope_note": "The source is a retrospective State Department database; updates are suspended and its inclusion/exclusion rules should be read before treating it as complete diplomatic service history.",
    }
    (RAW.parent / "state_department_principals_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
