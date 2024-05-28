import unittest
import os

from fin.rest import RestAPI, RestAPIBuilder, MANDATORY, FIXED

HTTPBIN_BASE_URL = "https://httpbingo.org"

SLOW_TESTS = os.environ.get("SLOW_TESTS")

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

class TestRestAPIParameters(unittest.TestCase):
    def api_with_method(self, method_name, param_name, req, extra, action):
        builder = RestAPIBuilder("MyAPIClass")
        builder.register(
            method_name,
            "get",
            {
                param_name: ( req, extra),
            }
        )
        api_class = builder()
        return api_class("http://example.com/api", get=action)

    def test_param_mandatory(self):
        called = False
        def fake_get(*args, **kwargs):
            nonlocal called
            called = True

        api = self.api_with_method("my_method", "x", MANDATORY, str, fake_get)
        api.my_method(x="abc")
        self.assertTrue(called)

    def test_param_fixed(self):
        x = None
        def fake_get(*args, params, **kwargs):
            nonlocal x
            x = params["x"]

        api = self.api_with_method("my_method", "x", FIXED, "hello", fake_get)
        api.my_method()
        self.assertEqual(x, "hello")
        

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
