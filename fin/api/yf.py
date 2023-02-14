""" An interface to some services provided by Yahoo Finance
"""

import urllib.parse
from datetime import datetime, timedelta
import requests

from fin.seq import table

UA="Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"

def get(url, _get=requests.get):
    headers = {
                'User-Agent': UA,
                }
    return _get(url, headers=headers)

# Historical data
HD_URI="https://query1.finance.yahoo.com/v7/finance/download/{TICKER:}?period1={FROM:}&period2={TO:}&interval=1d&events=history&includeAdjustedClose=true"

def historical_data(ticker, duration=timedelta(days=365), end=None):
    if end is None:
        end = datetime.now()
    start = end-duration
    url = HD_URI.format(
            TICKER=urllib.parse.quote(ticker),
            FROM=round(start.timestamp()),
            TO=round(end.timestamp()))

    r = get(url)
    if r.status_code != 200:
        raise Exception("Can't retrieve data at " + url + " status=" + str(r.status_code))

    t = table.table_from_csv(r.text.splitlines(), format="dnnnnni")
    return t

