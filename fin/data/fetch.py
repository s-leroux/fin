"""
Fetch data and populates the _data files.
"""
import re
import os
import time
import sqlite3
import urllib.parse
from bs4 import BeautifulSoup

import json
from pprint import pprint

from fin.api import investing
from fin.scrapper import Scrapper

PAGE_RE = re.compile("/[0-9]+")
EQUITY_TITLE_RE = re.compile("\s*(.*\S)\s*\(([^()]+)\)\s*$")

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

class DB:
    def __init__(self):
        self.con = sqlite3.connect("investing.db")
        self.init_db()

    def init_db(self):
        con = self.con
        con.execute("CREATE TABLE IF NOT EXISTS dump(url PRIMARY KEY, text NOT NULL)")

    def exists(self, url):
        try:
            cur = self.con.cursor()
            res = cur.execute("SELECT COUNT(*) FROM dump WHERE url = ?", (url,))
            count, = res.fetchone()

            return count != 0
        finally:
            cur.close()

    def store(self, url, text):
        with self.con as con:
            con.execute("DELETE FROM dump WHERE url = ?", (url,))
            con.execute("INSERT INTO dump(url, text) VALUES (?, ?)", (url, text))

    def close(self):
        self.con.close()

class Context:
    def __init__(self):
        self.db = DB()

    def close(self):
        self.db.close()

    def handle_equity(self, scrapper, url, text):
        # Check we have the required bits of information
        try:
            soup = BeautifulSoup(text, 'lxml')
            el_json = soup.find("script", type="application/json", id="__NEXT_DATA__")
            assert el_json is not None
        except Exception as e:
            print(f"Exception {e}\nwhile checking {url}")
            # Retry later and abort current processing
            scrapper.push(self.handle_equity, url)
            return

        self.save(url, text)

        return True

    def handle_index(self, scrapper, url, text):
        soup = BeautifulSoup(text, 'lxml')

        # Collect few data about the index itself
        # This also serves as a failsafe
        try:
            data = {} # Useless now
            el_heading = soup.find("h1")
            m = EQUITY_TITLE_RE.fullmatch(el_heading.string)
            data["shortName"], data["symbol"] = m.groups()
            data["market"] = find_key_value_span(soup, "Market:")
        except Exception as e:
            print(f"Exception {e}\nwhile checking {url}")
            # Retry later and abort current processing
            scrapper.push(self.handle_index, url)
            return

        # Retrieve the components in this page
        table = soup.find('table', id='cr1')
        for link in table.find_all('a', href=re.compile("^/equities/")):
            href = urllib.parse.urljoin(url, link["href"])
            if self.db.exists(href):
                print(f"Skipping {href}")
            else:
                scrapper.push(self.handle_equity, href)

        # Handle pagination
        for link in soup.find_all("a"):
            href = urllib.parse.urljoin(url, link.get("href", "/"))
            if href.startswith(url) and PAGE_RE.fullmatch(href[len(url):]):
                scrapper.push(self.handle_index, href)

        self.save(url, text)
        return True

    def save(self, url, text):
        print(f"Storing {url}")
        self.db.store(url, text)


def main():
    indice = (
            # https://www.investing.com terminology
            "france-40",
            "eu-stoxx50",
            "sbf-120",
            "us-30",
            "us-spx-500",
            "smallcap-2000",
            "nasdaq-composite",
            )

    scrapper = Scrapper()
    try:
        ctx = Context()
        for index in indice:
            scrapper.push(ctx.handle_index, investing.get_index_components_uri(index))

        scrapper.fetch()
    finally:
        ctx.close()
    """
    dir_name = os.path.dirname(__file__)
    for index in indice:
        it = investing.Index(index)
        it.fetch()
        record = it._data.copy()
        record["components"] = []
        for component in it.components:
            component.fetch()
            record["components"].append(component._data)

        file_name = os.path.join(dir_name, f"_{index}.json")
        with open(file_name, "wt") as f:
            json.dump(record, f, indent=4)
    """
if __name__ == "__main__":
    main()
