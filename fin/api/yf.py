""" An interface to some services provided by Yahoo Finance
"""

from fin.requests import get
from fin.seq import table
from fin.api.core import HistoricalData

# Historical data
YF_BASE_URI="https://query1.finance.yahoo.com/v7/finance"

def Client():
    class _Client(HistoricalData):
        def _historical_data(self, ticker, duration, end, _get=get):
            ONE_DAY=24*60*60
            uri = f"{YF_BASE_URI}/download/{ticker}"

            start = end-duration
            params = {
                    "period1": round(start.timestamp),
                    "period2": round(end.timestamp+ONE_DAY-1),
                    "interval": "1d",
                    "events": "history",
                    "includeAdjustedClose": "true",
                    }

            r = get(uri, params=params)
            if r.status_code != 200:
                raise Exception(f"Can't retrieve data at {uri} (status={r.status_code})")

            t = table.table_from_csv(
                    r.text.splitlines(),
                    name=ticker,
                    format="dnnnnni",
                    )
            return t

    return _Client()
