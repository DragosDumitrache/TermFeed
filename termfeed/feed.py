#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""TermFeed 0.0.11

Usage:
    feed
    feed <rss-url>
    feed -b
    feed -a <rss-url> [<category>]
    feed -d <rss-url>
    feed -t [<category>]
    feed -D <category>
    feed -R
    feed (-h | --help)
    feed --version

Options:
                  List feeds from the default category 'General' of your library.
    <URL>         List feeds from the provided url source.
    -b            Browse feed by category avaialble in the database file.
    -a URL        Add new url <rss-url> to database under [<category>] (or 'General' otherwise).
    -d URL        Delete <rss-url> from the database file.
    -t            See the stored categories in your library, or list the URLs stored under <category> in your library.
    -D TOPIC      Remove entire cateogry (and its urls) from your library.
    -R            Rebuild the library from the url.py
    -h --help     Show this screen.

"""


from __future__ import print_function
from optparse import OptionParser
from collections import OrderedDict
import sys
import webbrowser
import feedparser
import re

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

import termfeed.dbop as dbop

feed_hierarchy = []

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _connected():
    """check internet connect"""
    host = 'http://google.com'

    try:
        urlopen(host)
        return True
    except:
        return False


def open_page(url, title):
    print(bcolors.WARNING +
          '\topening ... {}\n'.format(title.encode('utf8')) + bcolors.ENDC)
    # open page in browser
    webbrowser.open(url)


def print_feed(zipped):
    for num, post in zipped.items():
        print(bcolors.OKGREEN + '[{}] '.format(num) + bcolors.ENDC, end='')
        print('{}'.format(post.title.encode('utf8')))


def print_desc(topic, txt):
    try:
        print(bcolors.WARNING + '\n\n{}:'.format(topic) + bcolors.ENDC)
    except UnicodeEncodeError:
        pass
    print(bcolors.BOLD + '\n\t{}'.format(txt.encode('utf8')) + bcolors.ENDC)


def open_it():
    try:
        txt = '\n\n\t Open it in browser ? [y/n] '
        try:
            q = raw_input(txt)  # python 2
        except NameError:
            q = input(txt)  # python 3

        print('\n')
        if q == 'y':
            return True
    except KeyboardInterrupt:
        print('\n')
        return False

def clean_txt(txt):
    """clean txt from e.g. html tags"""
    cleaned = re.sub(r'<.*?>', '', txt) # remove html
    cleaned = cleaned.replace('&lt;', '<').replace('&gt;', '>') # retain html code tags
    cleaned = cleaned.replace('&quot;', '"')
    cleaned = cleaned.replace('&rsquo;', "'")
    cleaned = cleaned.replace('&nbsp;', ' ') # italized text
    return cleaned

def _continue():
    try:

        msg = """\n\nPress: Enter to continue, ... [NUM] for short description / open a page, ... or CTRL-C to exit: """
        print(bcolors.FAIL + msg + bcolors.ENDC, end='')
        # kb is the pressed keyboard key
        try:
            kb = raw_input()
        except NameError:
            kb = input()
        return kb

    except KeyboardInterrupt:
        # return False
        exit()


def parse_feed(url):

    d = feedparser.parse(url)

    # validate rss URL
    if d.entries:
        return d
    else:
        print("INVALID URL feed: {}".format(url))
        return None


def fetch_feeds(url_entries):
    urls = url_entries.keys()
    for i, url in enumerate(urls):

        d = parse_feed(url)

        if d is None:
            continue  # to next url

        # feeds source
        l = len(urls) - 1
        print(bcolors.HEADER + "\n     {}/{} SOURCE>> {}\n".format(i, l, url) + bcolors.ENDC)
        # print out feeds
        url_entries[url]['unread'] = dict(enumerate(d.entries))
        def recurse(zipped):
            unread = zipped['unread']
            read = zipped['read']

            print_feed(unread)

            kb = _continue()  # keystroke listener

            if kb:
                user_selected = kb is not '' and kb in str(unread.keys())
                if user_selected:
                    # to open page in browser
                    link = unread[int(kb)].link
                    title = unread[int(kb)].title
                    try:
                        desc = unread[int(kb)].description
                        desc = clean_txt(desc)
                        print_desc(title, desc)
                    except AttributeError:
                        print('\n\tNo description available!!')

                    if open_it():
                        open_page(link, title)
                        read += [unread[int(kb)]]
                        unread.pop(int(kb), None)
                else:
                    print(
                        bcolors.BOLD + 'Invalid entry ... {} '.format(kb) + bcolors.ENDC)
                # repeat with same feeds and listen to kb again

                recurse(zipped)

        recurse(url_entries[url])


def topic_choice():
    topics = dbop.topics()

    feed_hierarchy = list(topics)
    for i, tag in enumerate(topics):
        print('{} {}'.format(i, feed_hierarchy[i]))

    try:
        m = '\nChoose the topic (number)? : '
        try: # python 2
            uin = raw_input(m)
        except NameError: # python 3
            uin = input(m)
        uin = int(uin)
        topic = feed_hierarchy[uin]
    except: # catch all exceptions
        print('\nInvalid choice!')
        topic = 'General'

    return dbop.read(topic)

def feed_browse(option, opt_str, value, parser):
    urls = topic_choice()
    fetch_feeds(urls)

def feed_add(option, opt_str, value, parser):
    add_link = parser.rargs[0]
    if len(parser.rargs) > 1:
        category = parser.rargs[1]
    else:
        category = False

    url = validate_feed(add_link)
    if category:
        dbop.add_link(url, category)
    else:
        dbop.add_link(url)


def feed_delete(option, opt_str, value, parser):
    dbop.remove_link(delete)

def feed_topics(option, opt_str, value, parser):
    category = parser.rargs
    if category:
        dbop.browse_links(category)
    else:
        dbop.print_topics()

def feed_remove_topic(option, opt_str, value, parser):
    dbop.delete_topic(parser.rargs[0])

def feed_refresh(option, opt_str, value, parser):
    dbop.rebuild_library()
    return "Refresh successful"

def feed_version(option, opt_str, value, parser):
    print("TermFeed 0.0.12 (Curtesy of Sire of Dragons and Aziz Alto)")

def validate_feed(url):
    if parse_feed(url):
        return url
    else:
        exit()

from .support.docopt import docopt


def main():
    flags_parser = OptionParser()
    flags_parser.add_option('-b', '--browse', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_browse, dest='output')
    flags_parser.add_option('-a', '--add', help='Add new url <rss-url> to database under [<category>] (or "General" otherwise)', action='callback', callback=feed_add, dest='output')
    flags_parser.add_option('-d', '--delete', help='Delete <rss-url> from the database file', action='callback', callback=feed_delete, dest='output')
    flags_parser.add_option('-t', '--topics', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_topics, dest='output')
    flags_parser.add_option('-D', '--removeTopic', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_remove_topic, dest='output')
    flags_parser.add_option('-R', '--refresh', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_refresh, dest='output')
    flags_parser.add_option('-v', '--version', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_version, dest='output')

    (options, args) = flags_parser.parse_args()

# start
if __name__ == '__main__':

    if not _connected():
        print('No Internet Connection!')
        exit()

    main()
