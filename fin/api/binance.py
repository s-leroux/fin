""" An interface to download data from https://data.binance.vision
"""
from io import BytesIO
from zipfile import ZipFile

from fin.requests import get
from fin.seq.serie import Serie
from fin.api.core import HistoricalData

from fin.datetime import asCalendarDate, asCalendarDateDelta

# Historical data
BINANCE_API_ENDPOINT="https://api.binance.com/api/v1/"

def historical_data_download(pair, duration, end):
    """ Download daily historical data.
    """
    result = []
    duration = asCalendarDateDelta(duration)
    end = asCalendarDate(end)
    start = end - duration
    end_point = f"{BINANCE_API_ENDPOINT}klines"

    start = int(start.timestamp * 1000)+1*24*3600000
    end = int(end.timestamp * 1000)+1*24*3600000-1
    while end > start:
        r = get(end_point, params=dict(
                startTime=start,
                endTime=end,
                symbol=pair,
                interval="1d",
            ))
        if r.status_code != 200:
            raise Exception(f"Can't retrieve data at {end_point} (status={r.status_code})")

        chunk = r.json()
        result += chunk
        start = chunk[-1][6]+1

    return result

def Client():
    class _Client(HistoricalData):
        def _historical_data(self, ticker, duration, end, _get=get, **kwargs):
            data = historical_data_download(ticker, duration, end)
            return Serie.from_rows(
                        ("Date", "Open", "High", "Low", "Close", "Volume"),
                        "mnnnnn",
                        data,
                        name=ticker,
                        )

    return _Client()
