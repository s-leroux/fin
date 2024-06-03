from fin.webapi import WebAPIBuilder, MANDATORY, OPTIONAL
from fin.datetime import asCalendarDate
from fin.utils.cache import SqliteCacheProvider as Cache

FMP_BASE_URL = "https://financialmodelingprep.com/api/"

fmp_web_api_builder = WebAPIBuilder("FMPWebAPI")

#
# Company Search
#
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

#
# Stock List
#
fmp_web_api_builder.register(
    "stock_list",
    "get",
    "v3/stock/list",
    {
    }
)

fmp_web_api_builder.register(
    "etf_list",
    "get",
    "v3/etf/list",
    {
    }
)

fmp_web_api_builder.register(
    "financial_statement_symbol_lists",
    "get",
    "v3/financial-statement-symbol-lists",
    {
    }
)

#
# Financial Statements
#
fmp_web_api_builder.register(
    "cash_flow_statement",
    "get",
    "v3/cash-flow-statement/{symbol}",
    {
        "symbol": ( MANDATORY, str),
        "period": ( OPTIONAL, str),
        "datatype": ( OPTIONAL, str),
        "limit": ( OPTIONAL, int),
    }
)

#
# Stock Historical Price
#
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
    def __init__(self, api_key, *, cache=None):
        super().__init__(FMP_BASE_URL, api_key)

        if cache is not None:
            if isinstance(cache, str):
                cache = Cache(cache)

            self._send_get_request = cache(self._send_get_request)



from fin.api.core import HistoricalData
from fin.seq.serie import Serie
from fin.seq import fc

def Client(api_key, **kwargs):
    api = FMPWebAPI(api_key, **kwargs)
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
