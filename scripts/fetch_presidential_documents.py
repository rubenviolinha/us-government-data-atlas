#!/usr/bin/env python3
"""Fetch keyless Federal Register presidential memoranda and determinations."""

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
TYPES = ["memorandum", "determination", "other"]
FIELDS = ["title", "abstract", "publication_date", "document_number", "html_url", "pdf_url", "json_url", "agencies"]


def fetch(url):
    request = Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read())


def main():
    retrieved_at = datetime.now(timezone.utc).isoformat()
    pages = []
    records = []
    for document_type in TYPES:
        params = [("conditions[type][]", "PRESDOCU"), ("conditions[presidential_document_type]", document_type), ("per_page", "1000"), ("order", "publication_date")]
        params.extend(("fields[]", field) for field in FIELDS)
        url = BASE + "?" + urlencode(params)
        while url:
            page = fetch(url)
            pages.append({"document_type": document_type, **page})
            for record in page.get("results", []):
                record["presidential_document_type"] = document_type
                record["source"] = record.get("json_url") or BASE
                records.append(record)
            url = page.get("next_page_url")
    records.sort(key=lambda row: (row.get("publication_date") or "", row.get("document_number") or ""))
    (RAW / "presidential-documents-federal-register.json").write_text(json.dumps({"retrieved_at": retrieved_at, "pages": pages}, indent=2) + "\n", encoding="utf-8")
    output = NORMALIZED / "presidential_documents.json"
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "retrieved_at": retrieved_at,
        "source": BASE,
        "queries": TYPES,
        "raw_file": "data/raw/presidential-documents-federal-register.json",
        "file": "data/normalized/presidential_documents.json",
        "records": len(records),
        "pages": len(pages),
        "counts_by_type": {document_type: sum(row["presidential_document_type"] == document_type for row in records) for document_type in TYPES},
    }
    (RAW / "presidential_document_retrieval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
