from urllib.request import urlopen

import feedparser


def connected():
    """check internet connect"""
    host = 'http://google.com'

    try:
        urlopen(host)
        return True
    except Exception:
        return False


def validate_feed(url):
    if parse_feed(url):
        return url
    else:
        exit()


def parse_feed(url):
    d = feedparser.parse(url)

    # validate rss URL
    if d.entries:
        return d
    else:
        print("INVALID URL feed: {}".format(url))
        return None
