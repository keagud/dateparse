"""
A pure Python library for parsing natural language date expressions.
No dependencies outside the standard library!

DateParser:
    The main public API for the library.
    Exposes methods for converting natural language time expressions into datetime.date objects.
    A stateful wrapper around DateProcessor that retains the given baseline date and other user 
    preferences.

DateProcessor:
    A grouping of utility functions for parsing dates. Lacks persistant state
"""

from .dateparser import DateParser
from .parser.date_processor import DateProcessor

__author__ = "keagud"
__contact__ = "keagud@protonmail.com"
__license__ = "GPL 3.0 or later"
