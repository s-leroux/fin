import os
import re

from fin import requests

class RestAPI:
    """
    Helper class to access REST APIs.
    """
    def __init__(self, base_url, api_key=None, *, api_key_param = "apikey"):
        self._base_url = base_url
        self._api_key = api_key
        self._api_key_param = api_key_param

    def url_for_endpoint(self, endpoint, path):
        url = endpoint
        base_url = self._base_url

        if not endpoint.startswith(base_url):
            url = f"{base_url}/{endpoint}"

        if path:
            url = f"{url}/{path}"

        return url

    def adjust_params(self, params):
        """
        Add API specific parameters to the request.

        Mostly intended to inject the API key into the request.
        """
        params = params.copy()
        api_key = self._api_key_param
        if api_key is not None:
            params[self._api_key_param] = self._api_key

        return params
    
    def _get(self, endpoint, path=None, *, params={}, options={}):
        """
        Send a GET request to the given API endpoint.
        """
        _get = options.get("get", requests.get)

        url = self.url_for_endpoint(endpoint, path)
        params = self.adjust_params(params)

        return _get(url, params=params)

def _get_wrapper(endpoint, param_list):
    # XXX This should add a layer of parameter checking
    def get(self, *args, **kwargs):
        return self._get(endpoint, *args, params=kwargs)

    return get

MANDATORY = True
OPTIONAL = False

VERSION_PREFIX_RE = re.compile("^v[0-9]+/")

class RestAPIBuilder:
    def __init__(self, class_name, *, api_base_class = RestAPI):
        self._class_name = class_name
        self._api_base_class = api_base_class
        self._methods = {}

    def __call__(self):
        methods = {
            name: method for name, method in self._methods.values()
        }
        return type(self._class_name, (self._api_base_class,), methods)

    def method_name_for_endpoint(self, endpoint):
        endpoint = VERSION_PREFIX_RE.sub("", endpoint)
        endpoint = endpoint.replace("-","_")
        return endpoint

    def register(self, endpoint, verb, param_list=None, *, method_name=None):
        if not method_name:
            method_name = self.method_name_for_endpoint(endpoint)

        if verb == "get":
            wrapper = _get_wrapper
        else:
            raise NotImplementedError(f"RestAPIBuildr.register is not implemented for the verb {verb!r}")

        method = (
                method_name,
                wrapper(endpoint, param_list)
            )

        self._methods[method_name] = method
        return method

FMP_BASE_URL = "https://financialmodelingprep.com/api/"

fmp_rest_api_builder = RestAPIBuilder("FMPRestAPI")
fmp_rest_api_builder.register(
    "v3/search-name",
    "get",
    {
        "query": ( MANDATORY, str),
        "limit": ( OPTIONAL, int),
        "exchange": ( OPTIONAL, str),
    }
)

class FMPRestAPI(fmp_rest_api_builder()):
    def __init__(self, api_key):
        super().__init__(FMP_BASE_URL, api_key)
