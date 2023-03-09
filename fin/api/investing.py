"""
An interface to some services provided by Investing.com
"""

import re
import time
import urllib.parse
from bs4 import BeautifulSoup

from datetime import datetime, timedelta
from fin.requests import get
from fin.seq import table

INDEX_COMPONENTS_URI = "https://www.investing.com/indices/{}-components"
EQUITY_URI = "https://www.investing.com/equities/{}"

PAGE_RE = re.compile("/[0-9]+")
TICKER_RE=re.compile("\((\w+)\)")
EQUITY_TITLE_RE = re.compile("\s*(.*\S)\s*\(([^()]+)\)\s*$")

# ======================================================================
# Utilities
# ======================================================================
def get_index_components_uri(name):
    return INDEX_COMPONENTS_URI.format(name)

def get_equity_uri(name):
    return EQUITY_URI.format(name)

def text(soup):
    return " ".join([s for s in soup.stripped_strings])

def find_key_value_span(soup, key, default=Ellipsis):
    """
    Get the value in `<span>key</span><span>value</span>` patterns.
    """
    el_value = None
    for el_key in soup.find_all("span"):
        if text(el_key) == key:
            el_value = el_key.find_next_sibling("span")
            break

    if not el_value:
        if default is not Ellipsis:
            return default
        raise KeyError(f"Key not found in document: {key}")

    return text(el_value)

# ======================================================================
# Equity
# ======================================================================
import json
from pprint import pprint

class Equity:
    """
    Interface to an equity page on Investing.com
    """
    def __init__(self, name):
        """
        Initialize an Equity instance.

        "name" is the site-specific name allowing to retrieve the equity page.
        """
        self._name = name
        self._loaded = False
        self._data = {}

    def fetch(self):
        """
        Load and parse the page on the remote website.
        """
        if self._loaded:
            return

        url = get_equity_uri(self._name)
        print("Fetching", url)

        while True:
            r = get(url, retry=7)
            if r.status_code == 200:
                break
            if r.status_code == 403:
                time.sleep(20)
                continue

            raise Exception("Can't retrieve data at " + url + " status=" + str(r.status_code))

        soup = BeautifulSoup(r.text, 'lxml')
        data = self._data

        el_json = soup.find("script", type="application/json", id="__NEXT_DATA__")
        page_state = json.loads(el_json.string)["props"]["pageProps"]["state"]
        page_state = json.loads(page_state)
        data_store = page_state["dataStore"]

        pprint(data_store["pageInfoStore"]["headers"])
        
        company_profile = data_store["companyProfileStore"]
        profile = company_profile["profile"]

        equity_store = data_store["equityStore"]
        equity_store = json.loads(equity_store)
        instrument = equity_store["instrument"]

        data["isin"] = instrument["underlying"]["isin"]
        data["description"] = profile["description"]
        data["exchange"] = instrument["exchange"]["exchange"]
        data["fullName"] = instrument["name"]["fullName"]
        data["shortName"] = instrument["name"]["shortName"]
        data["symbol"] = instrument["name"]["symbol"]

        self._loaded = True



# ======================================================================
# Index
# ======================================================================
_index_cache={}
class Index:
    """
    Interface to an index page on Investing.com
    """
    def __init__(self, name):
        """
        Initialize an Index instance.

        "name" is the site-specific name allowing to retrieve the index page.
        """
        self._name = name
        self._loaded = False
        self._data = {}

    def fetch(self):
        """
        Load and parse the page on the remote website.
        """
        if self._loaded:
            return

        baseurl = url = get_index_components_uri(self._name)
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

            while True:
                r = get(url, retry=7)
                if r.status_code == 200:
                    break
                if r.status_code == 403:
                    time.sleep(20)
                    continue

                raise Exception("Can't retrieve data at " + url + " status=" + str(r.status_code))

            visited.add(url)
            soup = BeautifulSoup(r.text, 'lxml')

            # Collect few data about the index itself
            data = self._data
            el_heading = soup.find("h1")
            m = EQUITY_TITLE_RE.fullmatch(el_heading.string)
            data["shortName"], data["symbol"] = m.groups()
            data["market"] = find_key_value_span(soup, "Market:")

            # Retrieve the components in this page
            table = soup.find('table', id='cr1')
            for link in table.find_all('a', href=re.compile("^/equities/")):
                # href = urllib.parse.urljoin(baseurl, link["href"])
                # stocks[href] = Equity(href)[link["title"], link.string]
                _, key = link["href"].rsplit("/", 1)
                stocks[key] = _index_cache.get(key, None)
                if stocks[key] is None:
                    _index_cache[key] = stocks[key] = Equity(key)

            # Handle pagination
            for link in soup.find_all("a"):
                href = urllib.parse.urljoin(baseurl, link.get("href", "/"))
                if href.startswith(baseurl) and PAGE_RE.fullmatch(href[len(baseurl):]):
                    pending.append(href)

        self.components = (*stocks.values(),)
        self._loaded = True
        return stocks

