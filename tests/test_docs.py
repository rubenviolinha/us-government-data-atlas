import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocsTests(unittest.TestCase):
    def test_docs_reference_api_contract(self):
        html = (ROOT / "docs" / "index.html").read_text()
        for endpoint in ("/health", "/catalog", "/dataset-groups", "/sources", "/access-requirements"):
            self.assertIn(endpoint, html)
        self.assertIn("field__contains", html)

    def test_catalog_summary_matches_catalog(self):
        catalog = json.loads((ROOT / "metadata" / "catalog.json").read_text())
        summary = json.loads((ROOT / "docs" / "catalog-summary.json").read_text())
        self.assertEqual(summary["dataset_file_count"], len(catalog["entries"]))
        self.assertGreater(summary["logical_group_count"], 0)
        self.assertGreater(summary["total_records"], 0)


if __name__ == "__main__":
    unittest.main()
