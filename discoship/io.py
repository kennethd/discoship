import functools
import requests

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"


def requests_session(**headers):
    """initializes a requests.Session suitable for scraping

    returns requests.Session object"""
    sess = requests.Session()
    # pe.usps.com, at least, rejects requests w/out User-Agent
    if 'User-Agent' not in headers.keys():
        headers['User-Agent'] = USER_AGENT
    sess.headers.update(headers)
    return sess


@functools.cache
def fetch_url(url, **headers):
    """fetches url & returns contents

    may raise any of the exceptions raised by requests library:
    https://docs.python-requests.org/en/latest/_modules/requests/exceptions/"""
    sess = requests_session(**headers)
    response = sess.get(url)
    return response.text

