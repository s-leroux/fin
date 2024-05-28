from fin.rest import RestAPIBuilder, MANDATORY, OPTIONAL

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
