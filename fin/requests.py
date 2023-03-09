"""
Utilities build on top of Python Requests
"""
import random
from time import sleep
import requests

# ======================================================================
# user agents
# ======================================================================
UAS = (
        "Mozilla/5.0 (Linux; Android 11; M2101K7AG Build/RKQ1.201022.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.5481.185 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/404.0.0.35.70;]",
        "Mozilla/5.0 (Linux; Android 11; RMX3269) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; TFY-LX3 Build/HONORTFY-L03CQ; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.5481.154 Mobile Safari/537.36 INAF/v1.6_281-android",
        "Mozilla/5.0 (Linux; Android 12; CPH2197 Build/SKQ1.210216.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.5481.154 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/404.0.0.35.70;]",
        "Mozilla/5.0 (Linux; Android 13; SM-A528B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.5481.154 Mobile Safari/537.36 INAF/v1.6_281-android",
        "Mozilla/5.0 (Linux; Android 4.4.2; A3-A10 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.84 Safari/537.36",
        "Mozilla/5.0 (Linux; U; Android 4.4.4; nl-nl; SM-T533 Build/KTU84P) AppleWebKit/537.16 (KHTML, like Gecko) Version/4.0 Safari/537.16",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:15.0) Gecko/20100101 Firefox/15.0.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.59.10 (KHTML, like Gecko) Version/5.1.9 Safari/534.59.10",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36 OPR/31.0.1889.200",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
        "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
        )

def _rotate_user_agent():
    while True:
        for ua in random.sample(UAS, k=len(UAS)):
            yield ua

def rotate_user_agent(_ua=_rotate_user_agent()):
    return next(_ua)

# ======================================================================
# Utilities
# ======================================================================
def cooldown(delay, _sleep=sleep):
    def _cooldown():
        nonlocal delay

        _sleep(delay)
        delay *= 3

    return _cooldown

# ======================================================================
# HTTP requests
# ======================================================================
def get(url, *, retry=5, headers=None, _get=requests.get):
    assert retry > 0 # Actually, it is not really a *re*try since the first try counts

    headers = {} if headers is None else headers.copy()

    wait = cooldown(0.5)
    while True:
        retry -= 1
        headers["User-Agent"] = rotate_user_agent()
        try:
            r = _get(url, headers=headers)
            status_code = r.status_code

            if status_code == 200:
                break
            if 500 > status_code >= 400 and status_code != 429:
                break
        except (requests.ConnectionError, requests.Timeout):
            pass

        if not retry:
            break

        print("Will retry", url)
        wait()

    return r
    
