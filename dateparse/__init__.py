"""
A pure Python library for parsing natural language date expressions.
No dependencies outside the standard library!

DateParser:
    The main public API for the library.
    Exposes methods for converting natural language time expressions into datetime.date objects

DateGroups:
    Exposes methods for grouping date tokens that combine into a single expression.
"""

from .dateparse import DateParser, DateGroups

__author__ = "keagud"
__contact__ = "keagud@protonmail.com"
__license__ = "GPL 3.0 or later"
