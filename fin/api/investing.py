"""
An interface to some services provided by Investing.com
"""

import re
import urllib.parse
from bs4 import BeautifulSoup

from datetime import datetime, timedelta
from fin.requests import get
from fin.seq import table

INDEX_COMPONENTS_URI = "https://www.investing.com/indices/nasdaq-composite-components"
PAGE_RE = re.compile("/[0-9]+")
TICKER_RE=re.compile("\((\w+)\)")

def get_index_components_uri(ticker):
    return INDEX_COMPONENTS_URI

def fetch_index_components(ticker):
    baseurl = url = get_index_components_uri(ticker)

    visited = set( ) # visited urls
    stocks = {} # the stock we have found
    pending = [ url ] # remaining urls to process

    while True:
        url = None
        while pending and url is None:
            url = pending.pop()
            if url in visited:
                url = None

        if url is None:
            break # done!

        print("Fetching", url)
        r = get(url)
        if r.status_code != 200:
            raise Exception("Can't retrieve data at " + url + " status=" + str(r.status_code))

        visited.add(url)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table', id='cr1')
        
        for link in table.find_all('a', href=re.compile("^/equities/")):
            href = urllib.parse.urljoin(baseurl, link["href"])
            stocks[href] = [link["title"], link.string]

        for link in soup.find_all("a"):
            href = urllib.parse.urljoin(baseurl, link.get("href", "/"))
            if href.startswith(baseurl) and PAGE_RE.fullmatch(href[len(baseurl):]):
                pending.append(href)

    # map each componenent to its ticker
    for url, record in stocks.items():
        corp = record[0]
        print("Fetching", url, "for", corp)
        r = get(url)
        if r.status_code != 200:
            raise Exception("Can't retrieve data at " + url + " status=" + str(r.status_code))

        soup = BeautifulSoup(r.text, 'lxml')
        for heading in soup.find_all("h1"):
            text = heading.string
            try:
                _, tail = text.split(corp)
            except ValueError:
                continue

            m = TICKER_RE.fullmatch(tail.strip())
            if m:
                record.append(m[1])
        
    for k, v in stocks.items():
        print(k,v)


