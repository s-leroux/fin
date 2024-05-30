from fin.containers.csv import CSV

from fin.webapi import WebAPIBuilder, FIXED, MANDATORY, OPTIONAL

AV_BASE_URL = "https://www.alphavantage.co"

# AlphaVantage API is not Rest:
# All methods will have the same access point named `query`, but will distinguish
# by their fixed parameter `function`
av_web_api_builder = WebAPIBuilder("AlphaVantageWebAPI")
av_web_api_builder.register(
    "time_series_daily_adjusted",
    "get",
    "query",
    {
        "function": ( FIXED, "TIME_SERIES_DAILY_ADJUSTED" ),
        "symbol": ( MANDATORY, str),
        "outputsize": ( OPTIONAL, str),
        "datatype": ( OPTIONAL, str),
    },
)

av_web_api_builder.register(
    "symbol_search",
    "get",
    "query",
    {
        "function": ( FIXED, "SYMBOL_SEARCH" ),
        "keywords": ( MANDATORY, str),
        "datatype": ( OPTIONAL, str),
    },
)

av_web_api_builder.register(
    "inflation",
    "get",
    "query",
    {
        "function": ( FIXED, "INFLATION" ),
        "datatype": ( FIXED, "csv" ),
    },
)

class AlphaVantageWebAPI(av_web_api_builder()):
    def __init__(self, api_key):
        super().__init__(AV_BASE_URL, api_key)

    def inflation(self, *args, **kwargs):
        return CSV.from_text(super().inflation(self, *args, *kwargs))
