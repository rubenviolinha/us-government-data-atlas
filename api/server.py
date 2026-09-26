#!/usr/bin/env python3
"""Dependency-free read-only API for the checked-in atlas releases."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "normalized"
CATALOG = ROOT / "metadata" / "catalog.json"
SOURCES = ROOT / "metadata" / "sources.json"
ACCESS_REQUIREMENTS = ROOT / "metadata" / "access_requirements.json"
OPENAPI = ROOT / "docs" / "openapi.json"
RELEASE_MANIFEST = ROOT / "metadata" / "release_manifest.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dataset_groups(catalog):
    """Return logical datasets, combining repository-safe ``_partN`` shards."""
    groups = {}
    for entry in catalog.get("entries", []):
        filename = entry["file"].removeprefix("data/normalized/")
        stem = filename.removesuffix(".json")
        match = re.match(r"^(.*)_part\d+$", stem)
        name = match.group(1) if match else stem
        group = groups.setdefault(name, {"name": name, "files": [], "records": 0, "shards": 0, "source_urls": []})
        group["files"].append(filename)
        group["records"] += entry.get("records", 0)
        group["shards"] += 1 if match else 0
        group["source_urls"] = sorted(set(group["source_urls"]) | set(entry.get("source_urls_sample", [])))
    return sorted(groups.values(), key=lambda item: item["name"])


def group_rows(group, catalog):
    files = next((item["files"] for item in dataset_groups(catalog) if item["name"] == group), None)
    if files is None:
        return None
    rows = []
    for filename in files:
        payload = read_json(DATA / filename)
        if isinstance(payload, list):
            rows.extend(payload)
    return rows


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=60")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            return self.send_json({"status": "ok"})
        if path == "/openapi.json":
            return self.send_json(read_json(OPENAPI))
        if path == "/release-manifest":
            return self.send_json(read_json(RELEASE_MANIFEST))
        if path in {"/", "/catalog", "/datasets"}:
            return self.send_json(read_json(CATALOG))
        if path == "/dataset-groups":
            groups = dataset_groups(read_json(CATALOG))
            query = parse_qs(urlparse(self.path).query)
            requested = query.get("group", [""])[0]
            if requested:
                groups = [group for group in groups if group["name"] == requested]
            return self.send_json({"groups": groups, "count": len(groups)})
        if path.startswith("/dataset-groups/"):
            group = unquote(path.removeprefix("/dataset-groups/"))
            if not group or "/" in group:
                return self.send_json({"error": "dataset group not found"}, 404)
            catalog = read_json(CATALOG)
            rows = group_rows(group, catalog)
            if rows is None:
                return self.send_json({"error": "dataset group not found"}, 404)
            query = parse_qs(urlparse(self.path).query)
            filters = {key: values[0] for key, values in query.items() if key not in {"limit", "offset"} and values}
            def matches(row):
                for key, value in filters.items():
                    if key.endswith("__contains"):
                        if value.lower() not in str(row.get(key.removesuffix("__contains"), "")).lower():
                            return False
                    elif str(row.get(key, "")).lower() != value.lower():
                        return False
                return True
            filtered = [row for row in rows if matches(row)]
            try:
                offset = max(0, int(query.get("offset", ["0"])[0]))
                limit = min(1000, max(1, int(query.get("limit", ["100"])[0])))
            except ValueError:
                return self.send_json({"error": "limit and offset must be integers"}, 400)
            page = filtered[offset:offset + limit]
            metadata = next(item for item in dataset_groups(catalog) if item["name"] == group)
            return self.send_json({"data": page, "total": len(filtered), "count": len(page), "offset": offset, "group": group, "source_urls": metadata["source_urls"]})
        if path == "/sources":
            return self.send_json(read_json(SOURCES))
        if path in {"/access-requirements", "/access_requirements"}:
            return self.send_json(read_json(ACCESS_REQUIREMENTS))
        if path.startswith("/datasets/"):
            filename = unquote(path.removeprefix("/datasets/"))
            allowed = {entry["file"].removeprefix("data/normalized/") for entry in read_json(CATALOG)["entries"]}
            if filename not in allowed or "/" in filename or not filename.endswith(".json"):
                return self.send_json({"error": "dataset not found"}, 404)
            payload = read_json(DATA / filename)
            query = parse_qs(urlparse(self.path).query)
            if not query:
                return self.send_json(payload)
            if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
                return self.send_json({"data": payload, "total": 1, "count": 1, "offset": 0})
            filters = {key: values[0] for key, values in query.items() if key not in {"limit", "offset"} and values}
            def matches(row):
                for key, value in filters.items():
                    if key.endswith("__contains"):
                        field = key.removesuffix("__contains")
                        if value.lower() not in str(row.get(field, "")).lower():
                            return False
                    elif str(row.get(key, "")).lower() != value.lower():
                        return False
                return True
            filtered = [row for row in payload if matches(row)]
            try:
                offset = max(0, int(query.get("offset", ["0"])[0]))
                limit = min(1000, max(1, int(query.get("limit", ["100"])[0])))
            except ValueError:
                return self.send_json({"error": "limit and offset must be integers"}, 400)
            return self.send_json({"data": filtered[offset:offset + limit], "total": len(filtered), "count": len(filtered[offset:offset + limit]), "offset": offset})
        return self.send_json({"error": "not found"}, 404)

    def log_message(self, *_args):
        return


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
