"""
Utilities build on top of Python Requests
"""
import requests

UA="Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"

def get(url, _get=requests.get):
    headers = {
                'User-Agent': UA,
                }
    return _get(url, headers=headers)
