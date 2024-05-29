import os
import re

from fin import requests

JSON_MIME_TYPES = (
    "application/json",
)

def mime_type(headers):
    """
    Extract the mimetype from an http response header.
    """
    content_type = headers["Content-Type"]
    content_type = content_type.split(";")[0].strip()
    return content_type

class RestAPI:
    """
    Helper class to access REST APIs.
    """
    def __init__(self, base_url, api_key=None, *, api_key_param = "apikey", get=None):
        self._base_url = base_url
        self._api_key = api_key
        self._api_key_param = api_key_param
        self._get = get or self._http_get

    def _url_for_endpoint(self, endpoint, path):
        url = endpoint
        base_url = self._base_url

        if not endpoint.startswith(base_url):
            url = f"{base_url}/{endpoint}"

        if path:
            url = f"{url}/{path}"

        return url

    def _adjust_params(self, params):
        """
        Add API specific parameters to the request.

        Mostly intended to inject the API key into the request.
        """
        params = params.copy()
        api_key = self._api_key_param
        if api_key is not None:
            params[self._api_key_param] = self._api_key

        return params
    
    def _http_get(self, endpoint, path=None, *, params={}, options={}):
        """
        Send a GET request to the given API endpoint.
        """
        _get = options.get("get", self._http_get_using_request)

        url = self._url_for_endpoint(endpoint, path)
        params = self._adjust_params(params)
        return _get(url, params=params)

    def _http_get_using_request(self, url, *, params):
        res = requests.get(url, params=params)

        status_code = res.status_code
        if status_code == 200:
            pass
        elif 400 <= status_code <= 499:
            raise HTTPClientError(res)
        else:
            raise HTTPServerError(res)

        return self._handle_http_response(res)

    def _handle_http_response(self, res):
        mt = mime_type(res.headers)
        if mt in JSON_MIME_TYPES:
            return res.json()

        return res.text

class ExtraParameterError(ValueError):
    def __init__(self, name):
        ValueError.__init__(self, f"Extra parameter: {name!r}")

class MissingParameterError(ValueError):
    def __init__(self, name):
        ValueError.__init__(self, f"Missing mandatory parameter: {name!r}")

def _filter_params(params, param_list):
    """
    Check the given parameters fits with the specifications.
    """
    params = params.copy()

    for name, specs in param_list.items():
        req = specs[0]
        if req == MANDATORY:
            if name not in params:
                raise MissingParameterError(name)
        elif req == FIXED:
            if name in params:
                raise ExtraParameterError(name)
            params[name] = specs[1]

    return params

def _get_wrapper(endpoint, param_list):
    # XXX This should add a layer of parameter checking
    def get(self, *args, **kwargs):
        params = _filter_params(kwargs, param_list)
        return self._get(endpoint, *args, params=params)

    return get

MANDATORY = True
OPTIONAL = False
FIXED = None

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

    def register(self, endpoint, verb, param_list={}, *, method_name=None):
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

