#!/usr/bin/env python
import subprocess

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = subprocess.run(['./version.sh'], capture_output=True, text=True).stdout

setup(
    name='TermFeed',
    description=('Browse, read, and open your favorite rss feed in the terminal.'),
    author='Dragos Dumitrache',
    url='https://github.com/dragosdumitrache/TermFeed',
    download_url='https://github.com/dragosdumitrache/TermFeed/archive/master.zip',
    license="MIT",
    author_email='dragosd2000@gmail.com',
    version=version,
    install_requires=['feedparser', 'click', 'simple-term-menu'],
    packages=['feed', 'feed.support'],
    scripts=[],
    entry_points={
        'console_scripts': [
            'feed = feed.feed:main'
        ]
    }
)
