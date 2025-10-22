import functools
import requests


@functools.cache
def fetch_url(url, verbose=False):
    """fetches url & returns contents

    may raise any of the exceptions raised by requests library:
    https://docs.python-requests.org/en/latest/_modules/requests/exceptions/"""
    response = requests.get(url)
    return response.text

