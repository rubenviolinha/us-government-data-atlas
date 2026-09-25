#!/usr/bin/env python3
"""Capture the National Archives' historical Electoral College result tables."""

from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"; NORMALIZED = ROOT / "data" / "normalized"
YEARS = [1789, 1792, 1796, 1800, 1804, 1808, 1812, 1816, 1820, 1824, 1828, 1832, 1836, 1840, 1844, 1848, 1852, 1856, 1860, 1864, 1868, 1872, 1876, 1880, 1884, 1888, 1892, 1896, 1900, 1904, 1908, 1912, 1916, 1920, 1924, 1928, 1932, 1936, 1940, 1944, 1948, 1952, 1956, 1960, 1964, 1968, 1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.tables = []; self.table = None; self.row = None; self.cell = None
    def handle_starttag(self, tag, attrs):
        if tag == "table": self.table = []
        elif tag == "tr" and self.table is not None: self.row = []
        elif tag in {"th", "td"} and self.row is not None: self.cell = []
    def handle_data(self, data):
        if self.cell is not None: self.cell.append(" ".join(data.split()))
    def handle_endtag(self, tag):
        if tag in {"th", "td"} and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split())); self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row: self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table); self.table = None


def main():
    rows = []; fetched = []
    for year in YEARS:
        url = f"https://www.archives.gov/electoral-college/{year}"
        parser = TableParser()
        try:
            parser.feed(urlopen(Request(url, headers={"User-Agent": "us-government-data-atlas/0.1"}), timeout=60).read().decode("utf-8", "replace"))
        except Exception:
            continue
        fetched.append(year)
        for table_index, table in enumerate(parser.tables):
            for row_index, cells in enumerate(table):
                rows.append({"election_year": year, "table_index": table_index, "row_index": row_index, "cells": cells, "source": url})
    NORMALIZED.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    filename = "electoral_college_results_1789_2024.json"
    (NORMALIZED / filename).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": "https://www.archives.gov/electoral-college/results", "format": "National Archives HTML tables", "records": len(rows), "elections": fetched, "file": "data/normalized/" + filename, "note": "Historical Electoral College tables are preserved row-wise to retain changing historical table layouts and candidate names; no API key used."}
    (RAW / "electoral_college_results_1789_2024_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
