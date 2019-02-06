#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='TermFeed',
    description=('Browse, read, and open your favorite rss feed in the terminal.'),
    author='Dragos Dumitrache',
    url='https://github.com/dragosdumitrache/TermFeed',
    download_url='https://github.com/dragosdumitrache/TermFeed/archive/master.zip',
    license="MIT",
    author_email='dragosd2000@gmail.com',
    version='0.0.11',
    install_requires=['feedparser', 'click'],
    packages=['termfeed', 'termfeed.support', 'termfeed.feed'],
    scripts=[],
    entry_points={
        'console_scripts': [
            'feed = termfeed.feed.feed:main'
        ]
    }
)
