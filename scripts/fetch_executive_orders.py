#!/usr/bin/env python3
"""Fetch executive-order metadata from the keyless Federal Register API."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORMALIZED.mkdir(parents=True, exist_ok=True)

BASE = "https://www.federalregister.gov/api/v1/documents.json"
FIELDS = ["executive_order_number", "title", "publication_date", "signing_date", "document_number", "html_url", "json_url", "abstract", "president"]


def fetch(url):
    request = Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read())


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    params = [("conditions[type][]", "PRESDOCU"), ("conditions[presidential_document_type]", "executive_order"), ("per_page", "1000"), ("order", "executive_order_number")]
    params.extend(("fields[]", field) for field in FIELDS)
    url = BASE + "?" + urlencode(params)
    pages = []
    while url:
        page = fetch(url)
        pages.append(page)
        url = page.get("next_page_url")
    records = [record for page in pages for record in page.get("results", [])]
    raw_path = RAW / "executive-orders-federal-register.json"
    raw_path.write_text(json.dumps({"retrieved_at": retrieved_at, "pages": pages}, indent=2) + "\n", encoding="utf-8")
    records.sort(key=lambda row: (str(row.get("executive_order_number") or ""), row.get("document_number") or ""))
    for record in records:
        record["source"] = record.get("json_url") or BASE
    output = NORMALIZED / "executive_orders.json"
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": BASE,
        "query": "presidential document type executive_order",
        "raw_file": "data/raw/executive-orders-federal-register.json",
        "file": "data/normalized/executive_orders.json",
        "records": len(records),
        "pages": len(pages),
    }
    (RAW / "executive_order_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
