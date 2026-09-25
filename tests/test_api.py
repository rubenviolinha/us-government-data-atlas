import json
import threading
import unittest
from http.client import HTTPConnection

from api.server import Handler, ThreadingHTTPServer


class ApiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.host, cls.port = cls.server.server_address

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get(self, path):
        connection = HTTPConnection(self.host, self.port, timeout=10)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        connection.close()
        return response.status, json.loads(body)

    def test_health(self):
        status, payload = self.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "ok")

    def test_filter_and_pagination(self):
        status, payload = self.get("/datasets/states.json?abbr=CA&limit=1")
        self.assertEqual(status, 200)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["data"][0]["name"], "California")

    def test_rejects_unlisted_dataset(self):
        status, _payload = self.get("/datasets/../../README.md")
        self.assertEqual(status, 404)

    def test_rejects_invalid_pagination(self):
        status, _payload = self.get("/datasets/states.json?limit=bad")
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
