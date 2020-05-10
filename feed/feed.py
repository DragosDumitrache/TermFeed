#!/usr/bin/env python
import os
import webbrowser

import click
from simple_term_menu import TerminalMenu

from feed.handlers import database
from feed.handlers.connectivity import connected, parse_feed, validate_feed
from feed.handlers.database import mark_read
from feed.handlers.output_handler import write, focus, clean_text

feed_hierarchy = []


def open_it():
    try:
        q = click.confirm('\n\n\t Open it in browser ?')
        return q
    except KeyboardInterrupt:
        return False


def feed_browse():
    topics = database.topics()

    feed_hierarchy = list(topics)
    feed_hierarchy.append('Exit')
    terminal_menu = TerminalMenu(feed_hierarchy, title='Select a topic')
    terminal_menu_exit = False

    while not terminal_menu_exit:
        os.system('clear')
        index = terminal_menu.show()
        topic = feed_hierarchy[index]

        if topic == 'Exit':
            terminal_menu_exit = True
            continue

        url_entries = database.read(topic)

        if url_entries:
            urls = list(url_entries.keys())
            urls.append('Back')
            feed_menu = TerminalMenu(urls, title='Select a feed')
            feed_menu_back = False
            while not feed_menu_back:
                os.system('clear')
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
                        os.system('clear')
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
                            desc = clean_text(desc)
                            write(f'\n\n{focus(title)}')
                            write(f'\n{desc}')

                        except AttributeError:
                            print('\n\tNo description available!!')

                        if open_it():
                            webbrowser.open(url)
                            read += [article]
                            # mark_read(topic, link, title)
                            unread.pop(article_index, None)


def feed_add(rss_url, category):
    url = validate_feed(rss_url)
    if category:
        database.add_link(url, category)
    else:
        database.add_link(url)


def feed_delete(rss_url):
    database.remove_link(rss_url)


def feed_topics(category=None):
    if category:
        database.browse_links(category)
    else:
        database.print_topics()


def feed_remove_topic(category):
    database.delete_topic(category)


def feed_refresh():
    database.rebuild_library()
    return "Refresh successful"


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
    if not connected():
        print('No Internet Connection!')
        exit()
    main()
