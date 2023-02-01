"""
A library for parsing natural language time expressions.
No dependencies outside the standard library!

Classes:
    DateParser:
        Defines a class for parsing multiple dates,
        while maintaining persistent user-defined configuration.

Functions:
    basic_parse
        Get a single date from a string, with its data in a NamedTuple

    basic_date_parse
        Get a single date from a string, as a datetime.date object

    parse_all
        Get all dates from a string as a list of NamedTuples

    parse_all_dates
        Get all dates from a string as a list of datetime.date objects

"""
from .dateparser import DateParser
from .parseutil import basic_parse, parse_all, parse_all_dates,basic_date_parse
