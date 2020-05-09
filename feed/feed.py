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
from simple_term_menu import TerminalMenu

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

from feed import dbop

feed_hierarchy = []


def fail(text):
    return click.style(text, fg='red')


def warn(text):
    return click.style(text, fg='yellow')


def success(text):
    return click.style(text, fg='green')


def focus(text):
    return click.style(text, fg='cyan')


def bold(text):
    return click.style(text, bold=True)


def _connected():
    """check internet connect"""
    host = 'http://google.com'

    try:
        urlopen(host)
        return True
    except Exception:
        return False


def open_page(url, title):
    click.echo(warn(f'{title}'))
    # open page in browser
    webbrowser.open(url)


def print_desc(topic, txt):
    click.echo(warn(f'\n\n{topic}'))
    click.echo(bold(f'\n\t{txt}'))


def open_it():
    try:
        q = click.confirm('\n\n\t Open it in browser ?')
        print('\n')
        if q:
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


def parse_feed(url):
    d = feedparser.parse(url)

    # validate rss URL
    if d.entries:
        return d
    else:
        print("INVALID URL feed: {}".format(url))
        return None


def feed_browse():
    topics = dbop.topics()

    feed_hierarchy = list(topics)
    feed_hierarchy.append('Exit')
    terminal_menu = TerminalMenu(feed_hierarchy, title='Select a topic')
    terminal_menu_exit = False

    while not terminal_menu_exit:
        index = terminal_menu.show()
        topic = feed_hierarchy[index]

        if topic == 'Exit':
            terminal_menu_exit = True
            continue

        url_entries = dbop.read(topic)

        if url_entries:
            urls = list(url_entries.keys())
            urls.append('Back')
            feed_menu = TerminalMenu(urls, title='Select a feed')
            feed_menu_back = False
            while not feed_menu_back:
                feed_choice = feed_menu.show()

                url = urls[feed_choice]
                if url == 'Back':
                    feed_menu_back = True
                    continue
                d = parse_feed(url)

                if d:
                    url_entries[url]['unread'] = dict(enumerate(d.entries))
                    unread = url_entries[url]['unread']
                    read = url_entries[url]['read']
                    available_titles = [m.title for m in unread.values()] + ['Back']
                    articles_menu = TerminalMenu(available_titles)
                    articles_menu_back = False
                    while not articles_menu_back:
                        article_index = articles_menu.show()

                        title = available_titles[article_index]
                        if title == 'Back':
                            articles_menu_back = True
                            continue

                        article = unread[article_index]

                        link = article.link
                        title = article.title

                        try:
                            desc = article.description
                            desc = clean_txt(desc)
                            print_desc(title, desc)
                        except AttributeError:
                            print('\n\tNo description available!!')

                        if open_it():
                            open_page(link, title)
                            read += [article]
                            unread.pop(article_index, None)


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


if __name__ == '__main__':
    if not _connected():
        print('No Internet Connection!')
        exit()
    main()
