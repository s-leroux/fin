from fin.webapi import WebAPIBuilder, MANDATORY, OPTIONAL

FMP_BASE_URL = "https://financialmodelingprep.com/api/"

fmp_web_api_builder = WebAPIBuilder("FMPWebAPI")
fmp_web_api_builder.register(
    "v3/search-name",
    "get",
    {
        "query": ( MANDATORY, str),
        "limit": ( OPTIONAL, int),
        "exchange": ( OPTIONAL, str),
    }
)

class FMPWebAPI(fmp_web_api_builder()):
    def __init__(self, api_key):
        super().__init__(FMP_BASE_URL, api_key)
