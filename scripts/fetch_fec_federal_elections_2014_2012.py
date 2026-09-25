#!/usr/bin/env python3
"""Fetch legacy FEC 2014 and 2012 federal election workbooks (.xls)."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

import xlrd

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
RAW = ROOT / "data" / "raw"
PUBLICATIONS = {
    2014: ("https://www.fec.gov/documents/1700/federalelections2014.xls", ("2014 US Senate Results by State", "2014 US House Results by State")),
    2012: ("https://www.fec.gov/documents/1691/federalelections2012.xls", ("2012 US House & Senate Resuts",)),
    2008: ("https://www.fec.gov/documents/1666/federalelections2008.xls", ("2008 House and Senate Results",)),
    2006: ("https://www.fec.gov/documents/1642/federalelections2006.xls", ("2006 US House & Senate Results",)),
    2004: ("https://www.fec.gov/documents/1625/2004congresults.xls", ("2004 US HOUSE & SENATE RESULTS",)),
}


def clean(value):
    if value == "":
        return None
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def parse_sheet(sheet, year, url, office_hint=None):
    headers = [str(value).strip().lower().replace(" ", "_").replace("#", "") if value is not None else "" for value in sheet.row_values(0)]
    rows = []
    for index in range(1, sheet.nrows):
        values = sheet.row_values(index)
        row = {header: clean(value) for header, value in zip(headers, values) if header and clean(value) is not None}
        # The 2006 workbook uses separate first/last-name columns and calls
        # the district column DISTRICT; newer publications already expose the
        # normalized candidate_name/d fields.  Normalize both layouts here.
        if not row.get("candidate_name"):
            row["candidate_name"] = row.get("last_name,_first") or " ".join(
                str(part).strip() for part in (row.get("first_name"), row.get("last_name")) if part
            )
        if not row.get("fec_id") or str(row.get("fec_id")).lower() == "n/a" or not row.get("candidate_name"):
            continue
        district = str(row.get("d") or row.get("district") or "")
        office = "senate" if district.upper() == "S" else (office_hint or "house")
        row.setdefault("d", district)
        row.update({"election_year": year, "office": office, "source": url, "source_sheet": sheet.name})
        rows.append(row)
    return rows


def fetch(year, url, sheet_names):
    request = Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"})
    with urlopen(request, timeout=300) as response:
        payload = response.read()
    workbook = xlrd.open_workbook(file_contents=payload)
    rows = []
    sheet_counts = {}
    for sheet_name in sheet_names:
        sheet = workbook.sheet_by_name(sheet_name)
        parsed = parse_sheet(sheet, year, url, "senate" if "Senate" in sheet_name else "house" if "House" in sheet_name else None)
        rows.extend(parsed)
        sheet_counts[sheet_name] = len(parsed)
    rows.sort(key=lambda row: (row["office"], str(row.get("state_abbreviation", "")), str(row.get("d", "")), row["fec_id"]))
    filename = f"fec_federal_elections_{year}.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": url, "format": "legacy Excel workbook", "sheets": sheet_counts, "records": len(rows), "file": "data/normalized/" + filename, "note": "Official certified federal election compilation; no API key used."}
    (RAW / f"fec_federal_elections_{year}_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    for year, (url, sheets) in PUBLICATIONS.items():
        fetch(year, url, sheets)


if __name__ == "__main__":
    main()
