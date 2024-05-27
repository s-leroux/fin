import unittest
import os

from fin.api.fmp import RestAPI, RestAPIBuilder, FMPRestAPI

HTTPBIN_BASE_URL = "https://httpbingo.org"

SLOW_TESTS = os.environ.get("SLOW_TESTS")
FMP_API_KEY = os.environ.get("FMP_API_KEY")

class TestRestAPI(unittest.TestCase):
    def test_get(self):
        request_args = ()
        request_kwargs = {}
        def fake_get(*args, **kwargs):
            return (args, kwargs)

        api_key = "myapikey"
        endpoint = "json"

        api = RestAPI(HTTPBIN_BASE_URL, api_key)
        request_args, request_kwargs = api._get(endpoint,
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
        test_cases = (
            "#0",
            "my_endpoint",
            "my_endpoint",

            "#1 Remove version prefix",
            "v3/search",
            "search",

            "#2 replace '-' by '_'",
            "v3/search-name",
            "search_name",
        )

        while test_cases:
            desc, endpoint, method, *test_cases = test_cases
            with self.subTest(desc=desc):
                builder = RestAPIBuilder("MyAPIClass")
                builder.register(endpoint, "get")

                self.assertIn(method, builder._methods)

                api = builder()

                self.assertIn(method, dir(api))

class TestRestAPIBuilderBuilt(unittest.TestCase):
    if SLOW_TESTS:
        def setUp(self):
            self.builder = RestAPIBuilder("MyAPIClass")

        def test_get(self):
            self.builder.register("range", "get")
            api_class = self.builder()
            api = api_class(HTTPBIN_BASE_URL)

            result = api.range("26")
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.text, "abcdefghijklmnopqrstuvwxyz")

        def test_get_with_param(self):
            self.builder.register("get", "get", {
                "x": ( True, int),
            })
            api_class = self.builder()
            api = api_class(HTTPBIN_BASE_URL)

            result = api.get(x="26")
            self.assertEqual(result.status_code, 200)
            json = result.json()
            self.assertSequenceEqual(json["args"]["x"], ["26"])

class TestFMPApi(unittest.TestCase):
    if SLOW_TESTS and FMP_API_KEY:
        def setUp(self):
            self.api = FMPRestAPI(FMP_API_KEY)

        def test_search_name(self):
            result = self.api.search_name(query="Xilam")
            self.assertEqual(result.status_code, 200)
            print(result.json())



