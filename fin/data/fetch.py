"""
Fetch data and populates the _data files.
"""
import re
import os
import time
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

class Context:
    def __init__(self, stem, destdir):
        self._stem = stem
        self._destdir = destdir

    def handle_equity(self, scrapper, url, text):
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
            scrapper.push(self.handle_equity, href)

        # Handle pagination
        for link in soup.find_all("a"):
            href = urllib.parse.urljoin(url, link.get("href", "/"))
            if href.startswith(url) and PAGE_RE.fullmatch(href[len(url):]):
                scrapper.push(self.handle_index, href)

        self.save(url, text)
        return True

    def save(self, url, text):
        stem = self._stem

        assert url.startswith(stem)

        filename = os.path.join(self._destdir, "_data", url[len(stem):].lstrip("/"))
        dirname = os.path.dirname(filename)
        os.makedirs(dirname, exist_ok=True)

        print(f"Saving {filename}")
        with open(filename, "wt") as f:
            f.write(text)


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
    ctx = Context("https://www.investing.com", os.path.dirname(__file__))
    for index in indice:
        scrapper.push(ctx.handle_index, investing.get_index_components_uri(index))
   
    scrapper.fetch()
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
