#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import re
import webbrowser

import click
import feedparser

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

from feed import dbop

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
    except Exception:
        return False


def open_page(url, title):
    print(bcolors.WARNING + '\topening ... {}\n'.format(title.encode('utf8')) + bcolors.ENDC)
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
        q = input(txt)  # python 3

        print('\n')
        if q == 'y':
            return True
    except KeyboardInterrupt:
        print('\n')
        return False


def clean_txt(txt):
    """clean txt from e.g. html tags"""
    cleaned = re.sub(r'<.*?>', '', txt)  # remove html
    cleaned = cleaned.replace('&lt;', '<').replace('&gt;', '>')  # retain html code tags
    cleaned = cleaned.replace('&quot;', '"')
    cleaned = cleaned.replace('&rsquo;', "'")
    cleaned = cleaned.replace('&nbsp;', ' ')  # italized text
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
                    print(bcolors.BOLD + 'Invalid entry ... {} '.format(kb) + bcolors.ENDC)
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
        try:  # python 2
            uin = raw_input(m)
        except NameError:  # python 3
            uin = input(m)
        uin = int(uin)
        topic = feed_hierarchy[uin]
    except:  # catch all exceptions
        print('\nInvalid choice!')
        topic = 'General'

    return dbop.read(topic)


def feed_browse():
    urls = topic_choice()
    fetch_feeds(urls)


def feed_add(rss_url, category):
    url = validate_feed(rss_url)
    if category:
        dbop.add_link(url, category)
    else:
        dbop.add_link(url)


def feed_delete(rss_url):
    dbop.remove_link(rss_url)


def feed_topics(category=None):
    if category:
        dbop.browse_links(category)
    else:
        dbop.print_topics()


def feed_remove_topic(category):
    dbop.delete_topic(category)


def feed_refresh():
    dbop.rebuild_library()
    return "Refresh successful"


def feed_version():
    print("TermFeed 0.0.12 (Curtesy of Sire of Dragons and Aziz Alto)")


def validate_feed(url):
    if parse_feed(url):
        return url
    else:
        exit()


CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help'], 'ignore_unknown_options': True}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def feed():
    pass


@feed.command()
def browse():
    """
    Browse feed by category available in the database file
    """
    feed_browse()


@feed.command()
@click.argument('rss-url')
@click.argument('category', default='General')
def add(rss_url, category='General'):
    """
    Add new url <rss-url> to database under [<category>][default: General]
    """
    feed_add(rss_url, category)


@feed.command()
@click.argument('rss-url')
def delete(rss_url):
    feed_delete(rss_url)


@feed.command()
@click.argument('category', required=False)
def topic(category):
    feed_topics(category)


@feed.command()
@click.argument('category', required=True)
def remove_topic(category):
    feed_remove_topic(category)


@feed.command()
def refresh():
    feed_refresh()


def main():
    feed()

"""
    # flags_parser = OptionParser()
    # flags_parser.add_option('-b', '--browse', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_browse, dest='output')
    # flags_parser.add_option('-a', '--add', help='Add new url <rss-url> to database under [<category>] (or "General" otherwise)', action='callback', callback=feed_add, dest='output')
    # flags_parser.add_option('-d', '--delete', help='Delete <rss-url> from the database file', action='callback', callback=feed_delete, dest='output')
    # flags_parser.add_option('-t', '--topics', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_topics, dest='output')
    # flags_parser.add_option('-D', '--removeTopic', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_remove_topic, dest='output')
    # flags_parser.add_option('-R', '--refresh', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_refresh, dest='output')
    # flags_parser.add_option('-v', '--version', help='Browse feed by category avaialble in the database file', action='callback', callback=feed_version, dest='output')

    # (options, args) = flags_parser.parse_args()
"""


if __name__ == '__main__':
    if not _connected():
        print('No Internet Connection!')
        exit()
    main()
