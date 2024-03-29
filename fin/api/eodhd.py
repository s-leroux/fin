"""
An interface to some API provided by eodhistoricaldata.com
"""

from fin.api.core import HistoricalData
from fin.requests import get
from fin.seq2 import serie
from fin.seq2 import fc

EODHD_BASE_URI="https://eodhistoricaldata.com/api"

def Client(api_token):
    class _Client(HistoricalData):
        def _historical_data(self, ticker, duration, end, _get=get):
            uri = f"{EODHD_BASE_URI}/eod/{ticker}"

            start = end-duration
            params = {
                    "from": str(start),
                    "to": str(end),
                    "fmt": "csv",
                    "api_token": api_token,
                    }

            r = get(uri, params=params)
            if r.status_code != 200:
                raise Exception(f"Can't retrieve data at {uri} (status={r.status_code})")

            t = serie.Serie.from_csv(
                    r.text.splitlines(),
                    name=ticker,
                    format="dnnnnni"
                ).select(
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    (fc.named("Adj Close"), "Adjusted_close"),
                    "Volume"
                )
            return t

    return _Client()
