"""
Utilities build on top of Python Requests
"""
import requests
from time import sleep

UA="Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"

def rotate_user_agent():
    return UA

def cooldown(delay, _sleep=sleep):
    def _cooldown():
        nonlocal delay

        _sleep(delay)
        delay *= 3

    return _cooldown

def get(url, *, retry=5, headers=None, _get=requests.get):
    assert retry > 0 # Actually, it is not really a *re*try since the first try counts

    headers = {} if headers is None else headers.copy()

    wait = cooldown(0.5)
    while True:
        retry -= 1
        headers["User-Agent"] = rotate_user_agent()
        try:
            r = _get(url, headers=headers)
            if r.status_code == 200:
                break
        except (requests.ConnectionError, requests.Timeout):
            pass

        if not retry:
            break

        print("Will retry", url)
        wait()

    return r
    
