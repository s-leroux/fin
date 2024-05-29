from fin.rest import RestAPIBuilder, FIXED, MANDATORY, OPTIONAL

AV_BASE_URL = "https://www.alphavantage.co"

# AlphaVantage API is not Rest, but we can stretch RestAPIBuilder to our needs
# All methods will have the same access point named `query`, but will distinguish
# by their fixed parameter `function`
av_rest_api_builder = RestAPIBuilder("AlphaVantageAPI")
av_rest_api_builder.register(
    "query",
    "get",
    {
        "function": ( FIXED, "TIME_SERIES_DAILY_ADJUSTED" ),
        "symbol": ( MANDATORY, str),
        "outputsize": ( OPTIONAL, str),
        "datatype": ( OPTIONAL, str),
    },
    method_name = "time_series_daily_adjusted"
)

av_rest_api_builder.register(
    "query",
    "get",
    {
        "function": ( FIXED, "SYMBOL_SEARCH" ),
        "keywords": ( MANDATORY, str),
        "datatype": ( OPTIONAL, str),
    },
    method_name = "symbol_search"
)

av_rest_api_builder.register(
    "query",
    "get",
    {
        "function": ( FIXED, "INFLATION" ),
        "datatype": ( FIXED, "csv" ),
    },
    method_name = "inflation"
)

class AlphaVantageAPI(av_rest_api_builder()):
    def __init__(self, api_key):
        super().__init__(AV_BASE_URL, api_key)
