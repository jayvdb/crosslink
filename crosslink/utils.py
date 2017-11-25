from __future__ import print_function

import sys

from hashlib import md5

import requests

from bs4 import BeautifulSoup

if sys.version_info[0] < 3:
    # Python 2.x
    from xmlrpclib import ServerProxy, Fault
    from urlparse import urlparse
    from urllib import urlencode, quote
else:
    # Python 3.x
    from xmlrpc.client import ServerProxy, Fault
    from urllib.parse import urlparse, urlencode, quote


def sanitize_email(email):
    """
    Returns an e-mail address in lower-case and strip leading and trailing
    whitespaces.

    >>> sanitize_email(' MyEmailAddress@example.com ')
    'myemailaddress@example.com'

    """
    return email.lower().strip()


def md5_hash(string):
    """
    Returns a md5 hash from a string.

    >>> md5_hash('myemailaddress@example.com')
    '0bc83cb571cd1c50ba6f3e8a78ef1346'

    """
    return md5(string.encode('utf-8')).hexdigest()


def fetch_head(url, headers=None, auth=None):
    r = requests.head(url, headers=headers, auth=auth)
    if r.status_code == 200:
        return r.headers


def fetch_xml(url, headers=None, auth=None):
    import xmltodict

    r = requests.get(url, headers=headers, auth=auth)
    if r.status_code != 200:
        return

    from xml.etree import ElementTree

    response = requests.get(url)

    try:
        data = xmltodict.parse(response.content)
    except Exception as e:
        print('Error parsing XML', response.content, file=sys.stderr)

    return data


def fetch_json(url, headers=None, auth=None):
    r = requests.get(url, headers=headers, auth=auth)
    if r.status_code != 200:
        return
    return r.json()
