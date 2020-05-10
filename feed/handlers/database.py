'''
This should be executed once to initialize the db from urls.py
'''
import pickle
from collections import OrderedDict
from os import path

from feed.urls import rss

homedir = path.expanduser('~')


def rebuild_library():
    database_init()
    print('created ".termfeed.db" in {}'.format(homedir))


# instantiate db if it's not created yet
if not path.exists(homedir + '/.termfeed.db'):
    rebuild_library()

# connect to db
db = open(path.join(homedir, '.termfeed.db'), 'rb')
d = pickle.load(db)


def database_init():
    d = OrderedDict()
    for topic in rss:
        links = rss[topic]
        d[topic] = {link: OrderedDict({'unread': [], 'read': []}) for link in links}

    with open(path.join(homedir, '.termfeed.db'), 'wb') as db:
        pickle.dump(d, db)


def update_database():
    global d
    pickle.dump(d, path.join(homedir, '.termfeed.db'))
    d = pickle.load(path.join(homedir, '.termfeed.db'))


def topics():
    return d.keys()


def read(topic):
    if topic in d.keys():
        return d[topic]
    else:
        return None


def mark_read(topic, link, title):
    if link not in d[topic][link]['read']:
        d[topic][link]['read'] += [title]
        d[topic][link]['unread'].remove(title)
        update_database()


def browse_links(topic):
    if topic in d.keys():
        links_entries = d[topic]
        links = links_entries.keys()
        print('{} resources:'.format(topic))
        for link in links:
            print('\t{}'.format(link))
    else:
        print('no category named {}'.format(topic))
        print_topics()


def print_topics():
    print('available topics: ')
    for t in topics():
        print('\t{}'.format(t))


def add_link(link, topic='General'):
    if topic in d.keys():
        if link not in d[topic]:
            # to add a new url: copy, mutates, store back
            temp = d[topic]
            temp.append(link)
            d[topic] = temp
            print('Updated .. {}'.format(topic))
        else:
            print('{} already exists in {}!!'.format(link, topic))
    else:
        print('Created new category .. {}'.format(topic))
        d[topic] = [link]


def remove_link(link):
    done = False
    for topic in topics():
        if link in d[topic]:
            d[topic] = [l for l in d[topic] if l != link]
            print('removed: {}\nfrom: {}'.format(link, topic))
            done = True

    if not done:
        print('URL not found: {}'.format(link))


def delete_topic(topic):
    if topic == 'General':
        print('Default topic "General" cannot be removed.')
        exit()
    try:
        del d[topic]
        print('Removed "{}" from your library.'.format(topic))
    except KeyError:
        print('"{}" is not in your library!'.format(topic))
        exit()


def add_topic(topic):
    if topic in d:
        print(f'Topic {topic} already exists')
    else:
        d[topic] = []
    exit()


if __name__ == '__main__':
    add_topic('Rust')
    pickle.dump(d, path.join(homedir, '.termfeed.db'))
    d = pickle.load(path.join(homedir, '.termfeed.db'))
