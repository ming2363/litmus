import unittest

from src.client import HttpClient
from src.models import HttpResponse, TransportError


class TestPublic(unittest.TestCase):
    def test_retry_then_succeed(self):
        attempts = []

        def fake_transport(req):
            attempts.append(req.timeout)
            if len(attempts) < 2:
                raise TransportError("temporary network issue")
            return HttpResponse(status_code=200, body="ok")

        client = HttpClient("https://api.example.com", timeout=2.5, max_retries=2, transport=fake_transport)
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "ok")
        self.assertEqual(attempts, [2.5, 2.5])

    def test_5xx_exhausts_retries(self):
        calls = [0]

        def always_503(_req):
            calls[0] += 1
            return HttpResponse(status_code=503, body="busy")

        client = HttpClient("https://api.example.com", timeout=1.0, max_retries=1, transport=always_503)
        with self.assertRaises(Exception):
            client.post("/jobs", body="{}")
        self.assertEqual(calls[0], 2)


if __name__ == "__main__":
    unittest.main()
