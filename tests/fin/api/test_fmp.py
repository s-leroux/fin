import unittest
import os

from fin.api.fmp import RestAPI, RestAPIBuilder

HTTPBIN_BASE_URL = "https://httpbingo.org"

class TestRestAPI(unittest.TestCase):
    def test_get(self):
        request_args = ()
        request_kwargs = {}
        def fake_get(*args, **kwargs):
            return (args, kwargs)

        api_key = "myapikey"
        endpoint = "json"

        api = RestAPI(HTTPBIN_BASE_URL, api_key)
        request_args, request_kwargs = api.get(endpoint,
            params=dict(
                query="AA",
            ),
            options=dict(
                get=fake_get,
            )
        )

        self.assertSequenceEqual(request_args, (
            f"{HTTPBIN_BASE_URL}/{endpoint}",
        ))
        self.assertEqual(request_kwargs["params"], {
            "apikey": api_key,
            "query": "AA",
        })

class TestRestAPIBuilder(unittest.TestCase):
    def test_register(self):
        builder = RestAPIBuilder("MyAPIClass")
        builder.register("my_endpoint", "get")

        self.assertIn("my_endpoint", builder._methods)

        api = builder()

        self.assertIn("my_endpoint", dir(api))

class TestRestAPIBuilderBuilt(unittest.TestCase):
    if os.environ.get("SLOW_TESTS"):
        def setUp(self):
            self.builder = RestAPIBuilder("MyAPIClass")

        def test_get(self):
            self.builder.register("range", "get")
            api_class = self.builder()
            api = api_class(HTTPBIN_BASE_URL)

            result = api.range("26")
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.text, "abcdefghijklmnopqrstuvwxyz")

