""" An interface to some services provided by Yahoo Finance
"""

import urllib.parse
from datetime import datetime, timedelta
import requests

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
    url = HD_URL.format(
            TICKER=urllib.parse.quote(args.ticker),
            FROM=round(period1.timestamp()),
            TO=round(period2.timestamp()))

    r = get(url)
    return r.text
