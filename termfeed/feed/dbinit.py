#!/usr/bin/env python

'''
This should be executed once to initialize the db from urls.py
'''
import pickle
from os import path
from collections import OrderedDict

from termfeed.urls import rss

homedir = path.expanduser('~')

d = OrderedDict()
for topic in rss:
    links = rss[topic]

    d[topic] = {link: OrderedDict({'unread': [], 'read': []}) for link in links}

with open(path.join(homedir, '.termfeed.db'), 'wb') as db:
    pickle.dump(d, db)
