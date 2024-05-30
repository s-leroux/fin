from fin.webapi import WebAPIBuilder, MANDATORY, OPTIONAL

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
        "from": ( OPTIONAL, str),
        "to": ( OPTIONAL, str),
        "serietype": ( OPTIONAL, str),
    }
)

class FMPWebAPI(fmp_web_api_builder()):
    def __init__(self, api_key):
        super().__init__(FMP_BASE_URL, api_key)
