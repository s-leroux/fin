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
        return CSV.from_text(super().inflation(self, *args, **kwargs))

    def time_series_daily_adjusted(self, *args, **kwargs):
        result = super().time_series_daily_adjusted(self, *args, **kwargs)
        if type(result) is str:
            # We assume it is CSV
            result = CSV.from_text(result)
        elif "Information" in result:
            # AlphaVantage returns "error" with 200 status code and a specific JSON record
            raise ValueError(result["Information"])

        return result

from fin.api.core import HistoricalData
from fin.seq.serie import Serie

def Client(api_key):
    api = AlphaVantageWebAPI(api_key)
    class _Client(HistoricalData):
        def _historical_data(self, ticker, duration, end, **kwargs):
            start = end-duration+dict(days=1)
            params = {
                "symbol": ticker,
                "outputsize": "full",
                "datatype": "csv",
            }

            csv = api.time_series_daily_adjusted(**params)
            fields = ("date", "open", "high", "low", "close", "adjusted close", "volume")
            return Serie.from_rows(
                    fields,
                    "dnnnnni",
                    csv,
                    conv=True,
                ).select(
                    (fc.named("Date"), "date"),
                    (fc.named("Open"), "open"),
                    (fc.named("High"), "high"),
                    (fc.named("Low"), "low"),
                    (fc.named("Close"), "close"),
                    (fc.named("Adj Close"), "adjusted close"),
                    (fc.named("Volume"), "volume"),
                )

    return _Client()

