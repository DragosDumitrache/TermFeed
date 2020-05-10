import re
import textwrap

import click


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


def write(args):
    click.echo(args)


def clean_text(text):
    """clean txt from e.g. html tags"""
    cleaned = re.sub(r'<.*?>', '', text)  # remove html
    cleaned = cleaned.replace('&lt;', '<').replace('&gt;', '>')  # retain html code tags
    cleaned = cleaned.replace('&quot;', '"')
    cleaned = cleaned.replace('&rsquo;', "'")
    cleaned = cleaned.replace('&nbsp;', ' ')  # italized text

    return textwrap.fill(cleaned, width=100)
