from time import time, sleep
from collections import deque
from fin.requests import get

DEFAULT_RETRY=20
MIN_RETRY_DELAY=30

# ======================================================================
# Multiprocessing
# ======================================================================
import multiprocessing

def _worker(n, handler, from_parent, to_parent):
    quit = False
    try:
        while not quit:
            cid, command, *args = from_parent.get()
            def post(command, *args):
                to_parent.put_nowait((cid, command, *args))

            if command == "QUIT":
                quit = True
            elif command == "PRINT":
                print(f"Worker {n} says:", *args)
            else:
                handler(post, command, *args)

            post("DONE") # Wake up the manager at least one time
    finally:
        to_parent.put((0, "BYE", n))

def spawn_workers(n, handler, from_parent, to_parent):
    processes = [
        multiprocessing.Process(target=_worker, args=(i, handler, from_parent, to_parent,))
        for i in range(n)
        ]
    for process in processes:
        process.start()

    return processes

class Manager:
    def __init__(self, n, handler):
        from_parent = self.from_parent = multiprocessing.Queue()
        to_parent = self.to_parent = multiprocessing.Queue()
        self.workers = spawn_workers(n, handler, from_parent, to_parent)
        self.running = n
        self.cid = 0

    def close(self):
        for worker in self.workers:
            # worker.close() # python >3.7 only
            worker.join()

    def shutdown(self):
        for i in range(self.running):
            self.post("QUIT")

    def post(self, command, *args):
        self.cid += 1
        self.from_parent.put_nowait((self.cid, command, *args))

        return self.cid

    def wait_next_action(self):
        cid, action, *args = self.to_parent.get()
        print("Receiving", action)

        if action == "BYE":
            self.running -= 1
        else:
            self.do_command(cid, action, *args)

        return self.running != 0

    def do_command(self, cid, command, *args):
        pass

# ======================================================================
# Web scrapper
# ======================================================================
def _scrapper_download(post, prec, url, counter):
    remaining = MIN_RETRY_DELAY-(time()-prec)
    if remaining > 0:
        print(f"Sleeping {round(0.5+remaining)}s")
        sleep(remaining)

    try:
        print(f"Fetching {url}")
        r = get(url)
        if r.status_code != 200:
            raise Exception(f"status {r.status_code}")
        post("OK", r.text)
    except Exception as e:
        print(f"Error {e} while retrieving {url} [{counter}]")
        post("RETRY", time(), url, counter)

def _scrapper_worker(post, command, *args):
    if command == "DOWNLOAD":
        _scrapper_download(post, *args)
    else:
        print(f"Unknown command: {command}", *args)

SCRAPPER_WORKER_COUNT = 4
class Scrapper(Manager):
    def __init__(self):
        super().__init__(SCRAPPER_WORKER_COUNT, _scrapper_worker)
        self._queued = set()
        self.pending = {}

    def push(self, handler, *urls):
        for url in urls:
            if url not in self._queued:
                self._queued.add(url)
                cid = self.post("DOWNLOAD", 0, url, 0)
                self.pending[cid] = (handler, url)

    def do_command(self, cid, command, *args):
        if command == "RETRY":
            self.do_retry(cid, *args)
        elif command == "OK":
            self.do_ok(cid, *args)

    def do_retry(self, cid, t, url, counter):
        new_cid = self.post("DOWNLOAD", t, url, counter+1)
        self.pending[new_cid] = self.pending.pop(cid)

    def do_ok(self, cid, text):
        handler, url = self.pending.pop(cid)
        try:
            if handler(self, url, text):
                return
        except Exception as e:
            print(e)

        # Oops. Retry
        self._queued.remove(url)
        self.push(handler, url)

    def fetch(self):
        while self.pending and self.wait_next_action():
            pass
        print("Shutting down workers")
        self.shutdown()
        while self.wait_next_action():
            pass

        print("Shutdown completed")
