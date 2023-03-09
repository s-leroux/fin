from time import time, sleep
from collections import deque
from fin.requests import get

DEFAULT_RETRY=20
MIN_RETRY_DELAY=30

class Scrapper:
    def __init__(self):
        self._queue = deque()
        self._visited = set()

    def push(self, handler, *urls):
        for url in urls:
            self._queue.append((0, handler, url, DEFAULT_RETRY))

    def fetch(self):
        while self._queue:
            prec, handler, url, retry = self._queue.popleft()
            if url in self._visited:
                continue

            remaining = MIN_RETRY_DELAY-(time()-prec)
            if remaining > 0:
                print(f"Sleeping {round(0.5+remaining)}s")
                sleep(remaining)

            try:
                print(f"Fetching {url}")
                r = get(url)
                if r.status_code != 200:
                    raise Exception(f"status {r.status_code}")
            except Exception as e:
                print(f"Error {e} while retrieving {url} [{retry}]")
                if retry > 0:
                    self._queue.append((time(), handler, url, retry-1))
                    continue
                else:
                    raise

            if handler(self, url, r.text):
                self._visited.add(url)

