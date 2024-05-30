from fin.containers.csv import CSV

from fin.webapi import WebAPIBuilder, FIXED, MANDATORY, OPTIONAL

AV_BASE_URL = "https://www.alphavantage.co"

# AlphaVantage API is not Web, but we can stretch WebAPIBuilder to our needs
# All methods will have the same access point named `query`, but will distinguish
# by their fixed parameter `function`
av_web_api_builder = WebAPIBuilder("AlphaVantageWebAPI")
av_web_api_builder.register(
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

av_web_api_builder.register(
    "query",
    "get",
    {
        "function": ( FIXED, "SYMBOL_SEARCH" ),
        "keywords": ( MANDATORY, str),
        "datatype": ( OPTIONAL, str),
    },
    method_name = "symbol_search"
)

av_web_api_builder.register(
    "query",
    "get",
    {
        "function": ( FIXED, "INFLATION" ),
        "datatype": ( FIXED, "csv" ),
    },
    method_name = "inflation"
)

class AlphaVantageWebAPI(av_web_api_builder()):
    def __init__(self, api_key):
        super().__init__(AV_BASE_URL, api_key)

    def inflation(self, *args, **kwargs):
        return CSV.from_text(super().inflation(self, *args, *kwargs))
