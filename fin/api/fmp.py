from fin.webapi import WebAPIBuilder, MANDATORY, OPTIONAL
from fin.datetime import asCalendarDate

FMP_BASE_URL = "https://financialmodelingprep.com/api/"

fmp_web_api_builder = WebAPIBuilder("FMPWebAPI")
fmp_web_api_builder.register(
    None,
    "get",
    "v3/search-name",
    {
        "query": ( MANDATORY, str),
        "limit": ( OPTIONAL, int),
        "exchange": ( OPTIONAL, str),
    }
)

fmp_web_api_builder.register(
    "historical_price_full",
    "get",
    "v3/historical-price-full/{symbol}",
    {
        "symbol": ( MANDATORY, str),
        "from": ( OPTIONAL, asCalendarDate),
        "to": ( OPTIONAL, asCalendarDate),
        "serietype": ( OPTIONAL, str),
    }
)

class FMPWebAPI(fmp_web_api_builder()):
    def __init__(self, api_key):
        super().__init__(FMP_BASE_URL, api_key)


from fin.api.core import HistoricalData
from fin.seq.serie import Serie
from fin.seq import fc

def Client(api_key):
    api = FMPWebAPI(api_key)
    class _Client(HistoricalData):
        def _historical_data(self, ticker, duration, end, **kwargs):
            start = end-duration+dict(days=1)
            params = {
                "from": start,
                "to": end,
                "symbol": ticker,
            }

            json = api.historical_price_full(**params)
            return Serie.from_dictionaries(
                    ("date", "open", "high", "low", "close", "adjClose", "volume"),
                    "dnnnnni",
                    reversed(json["historical"]),
                    conv=True,
                ).select(
                    (fc.named("Date"), "date"),
                    (fc.named("Open"), "open"),
                    (fc.named("High"), "high"),
                    (fc.named("Low"), "low"),
                    (fc.named("Close"), "close"),
                    (fc.named("Adj Close"), "adjClose"),
                    (fc.named("Volume"), "volume"),
                )

    return _Client()
