""" An interface to some services provided by Yahoo Finance
"""

import urllib.parse
from datetime import datetime, timedelta
from fin.requests import get

from fin.seq import table

# Historical data
HD_URI="https://query1.finance.yahoo.com/v7/finance/download/{TICKER:}?period1={FROM:}&period2={TO:}&interval=1d&events=history&includeAdjustedClose=true"

def historical_data_url(ticker, duration=timedelta(days=365), end=None):
    if end is None:
        end = datetime.now()
    start = end-duration
    url = HD_URI.format(
            TICKER=urllib.parse.quote(ticker),
            FROM=round(start.timestamp()),
            TO=round(end.timestamp()))

    return url

def historical_data(ticker, duration=timedelta(days=365), end=None, select=None):
    url = historical_data_url(ticker, duration, end)
    r = get(url)
    if r.status_code != 200:
        raise Exception("Can't retrieve data at " + url + " status=" + str(r.status_code))

    t = table.table_from_csv(r.text.splitlines(), name=ticker, format="dnnnnni", select=select)
    return t

