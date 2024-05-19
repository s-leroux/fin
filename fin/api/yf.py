""" An interface to some services provided by Yahoo Finance
"""
from fin.requests import get
from fin.seq.serie import Serie
from fin.api.core import HistoricalData

# Historical data
YF_BASE_URI="https://query1.finance.yahoo.com/v7/finance"

def Client():
    class _Client(HistoricalData):
        def _historical_data(self, ticker, duration, end, _get=get, **kwargs):
            ONE_DAY=24*60*60
            uri = f"{YF_BASE_URI}/download/{ticker}"

            start = end-duration
            start_ts = start.timestamp+ONE_DAY
            end_ts = end.timestamp+ONE_DAY-1
            t = None

            while True:
                params = {
                        "period1": round(start_ts),
                        "period2": round(end_ts),
                        "interval": "1d",
                        "events": "history",
                        "includeAdjustedClose": "true",
                        }

                r = get(uri, params=params)
                if r.status_code != 200:
                    raise Exception(f"Can't retrieve data at {uri} (status={r.status_code})")
                tmp = Serie.from_csv(
                        r.text.splitlines(),
                        name=ticker,
                        format="dnnnnni",
                        )
                t = tmp if t is None else t.union(tmp)

                start_ts += 360*ONE_DAY
                if start_ts >= end_ts:
                    break

            return t

    return _Client()
