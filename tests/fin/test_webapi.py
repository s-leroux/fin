import unittest
import os

from fin.webapi import (
    WebAPI, WebAPIBuilder,
    MANDATORY, FIXED, OPTIONAL,
    ExtraParameterError, MissingParameterError,
)

HTTPBIN_BASE_URL = "https://httpbingo.org"

SLOW_TESTS = os.environ.get("SLOW_TESTS")

def fake_get(*args, **kwargs):
    return (args, kwargs)

class TestWebAPI(unittest.TestCase):
    def test_get(self):
        request_args = ()
        request_kwargs = {}
        def fake_get(*args, **kwargs):
            return (args, kwargs)

        api_key = "myapikey"
        endpoint = "json"

        api = WebAPI(HTTPBIN_BASE_URL, api_key)
        request_args, request_kwargs = api._get(endpoint,
            params=dict(
                query="AA",
            ),
            options=dict(
                transport=fake_get,
            )
        )

        self.assertSequenceEqual(request_args, (
            f"{HTTPBIN_BASE_URL}/{endpoint}",
        ))
        self.assertEqual(request_kwargs["params"], {
            "apikey": api_key,
            "query": "AA",
        })

    def test_url_parameters(self):
        endpoint = "base64/{encoded}"
        params = {
            "encoded": "aHR0cGJpbmdvLm9yZw==",
        }

        api = WebAPI(HTTPBIN_BASE_URL)
        args, kwargs = api._get(endpoint,
            params=params,
            options=dict(
                transport=fake_get,
            )
        )

        self.assertEqual(args[0], f"{HTTPBIN_BASE_URL}/base64/{params['encoded']}")
        self.assertNotIn("encoded", kwargs)



class TestWebAPIBuilder(unittest.TestCase):
    def test_register(self):
        test_cases = (
            "#0",
            "my_endpoint",
            "my_endpoint",

            "#1 Remove version prefix",
            "search",
            "v3/search",

            "#2 replace '-' by '_'",
            "search_name",
            "v3/search-name",
        )

        while test_cases:
            desc, method, endpoint, *test_cases = test_cases
            with self.subTest(desc=desc):
                builder = WebAPIBuilder("MyAPIClass")
                builder.register(method, "get", endpoint)

                self.assertIn(method, builder._methods)

                api = builder()

                self.assertIn(method, dir(api))

class TestWebAPIParameters(unittest.TestCase):
    def api_with_method(self, method_name, param_name, req, extra, action):
        builder = WebAPIBuilder("MyAPIClass")
        builder.register(
            method_name,
            "get",
            method_name,
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

    def test_param_mandatory_missing(self):
        called = False
        def fake_get(*args, **kwargs):
            nonlocal called
            called = True

        api = self.api_with_method("my_method", "x", MANDATORY, str, fake_get)

        with self.assertRaises(TypeError):
            api.my_method()
        self.assertFalse(called)

    def test_param_fixed(self):
        x = None
        def fake_get(*args, params, **kwargs):
            nonlocal x
            x = params["x"]

        api = self.api_with_method("my_method", "x", FIXED, "hello", fake_get)
        api.my_method()
        self.assertEqual(x, "hello")

    def test_param_fixed_duplicate(self):
        called = False
        def fake_get(*args, **kwargs):
            nonlocal called
            called = True

        api = self.api_with_method("my_method", "x", FIXED, "hello", fake_get)
        with self.assertRaises(TypeError):
            api.my_method(x=1)
        self.assertFalse(called)

    def test_param_type_conv(self):
        x = None
        def fake_get(*args, params, **kwargs):
            nonlocal x
            x = params["x"]

        api = self.api_with_method("my_method", "x", OPTIONAL, int, fake_get)
        api.my_method(x="12")
        self.assertEqual(x, 12)

    def test_param_type_check(self):
        called = False
        def fake_get(*args, **kwargs):
            nonlocal called
            called = True

        api = self.api_with_method("my_method", "x", OPTIONAL, int, fake_get)
        with self.assertRaises(ValueError):
            api.my_method(x="a")
        self.assertFalse(called)
        

class TestWebAPIBuilderBuild(unittest.TestCase):
    if SLOW_TESTS:
        def setUp(self):
            self.builder = WebAPIBuilder("MyAPIClass")

        def test_get(self):
            self.builder.register("range", "get", "range")
            api_class = self.builder()
            api = api_class(HTTPBIN_BASE_URL)

            result = api.range("26")
            self.assertEqual(result, "abcdefghijklmnopqrstuvwxyz")

        def test_get_with_param(self):
            self.builder.register("get", "get", "get", {
                "x": ( True, int),
            })
            api_class = self.builder()
            api = api_class(HTTPBIN_BASE_URL)

            result = api.get(x="26")
            print(result)
            self.assertSequenceEqual(result["args"]["x"], ["26"])
