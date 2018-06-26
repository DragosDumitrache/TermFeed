#!/usr/bin/env python

# This should be exectued once to initialize the db from urls.py

import shelve
import pickle
from os import path
from collections import OrderedDict

from termfeed.urls import rss

homedir = path.expanduser('~')

# initiate database datafile
# d = shelve.open(path.join(homedir, '.termfeed'))

# dump urls.py into rss_shelf.dbd = [
d = OrderedDict()
for topic in rss:
    links = rss[topic]

    d[topic] = {link:OrderedDict({'unread': [], 'read': []}) for link in links}

pickle.dump(d, open(path.join(homedir, '.termfeed.db'), 'wb'))

# d.close()
