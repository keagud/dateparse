
"""
Defines the API for the main operations exposed by the Dateparse package,
via the DateParser class.
"""

from datetime import date
from pprint import pformat
from typing import Iterable
from typing import Iterator
from calendar import monthrange


from parser.parse_functions import absolute_functions_index
from parser.parse_functions import relative_functions_index

from parser.date_processor import DateProcessor


class DateParser:
    """
    The intended interface for converting a natural language date expression into a date
    (datetime.date) object.

    Attributes:
    ------------

    current_date: datetime.date
        The date to be used to determine how to parse expressions that require temporal context,
        e.g. "A week from this Sunday", "In four days"

        If not passed into the constructor, defaults to the current date
        (datetime.date.today()).

    named_days: dict[str,str]
        Aliases for date expressions; occurrences of each key will be substituted for
        the corresponding value before parsing begins.

        This allows for dates of personal importance to be named directly.
        e.g. {'my birthday': 'october 17'} will cause the string 'my birthday'
        to act as an alias for 'october 17'


    Methods:
    ___________

    __init__(current_date: datetime.date | None = None,
        named_days: dict[str,str] | None = None, allow_past: bool = False) -> None:
        Constructor for creating a new DateParser object.

    sub_named_days(text:str) -> str:
        Substitutes each occurrence of a defined alias from named_days
        (both passed in at init time or included from the defaults list)
        with its corresponding replacement string.

    group_match_tokens(text:str) -> DateGroups:
        Locates expressions in the text that match a known date pattern, and groups
        consecutive expressions together as a DateGroups object.

    parse_date_match(date_match: DateMatch) -> datetime.date | DateValues
        For the given DateMatch object, call its to_date() method and return the result.
        If the DateMatch represents a modifier rather than an absolute date,
        returns as a DateValues, otherwise returns a datetime.date


    parse_tokens(match_iter: Iterable[DateMatch]) -> date:
        Returns the date created from the summation of DateMatch objects referring to
        DeltaDateExpressions, (e.g. 'a week from') from the match_iter iterable, until an
        AbsoluteDateExpression (an expression than can unambiguously be converted to a date,
        potentially using the current date as a reference) is encountered.

        In practice, this means parse_tokens will take an iterable like:
            ['a week from', 'the day after', 'Tuesday', 'foo']
        and combine the contents up to and including 'Tuesday',
        which it returns as a datetime.date

    extract_and_parse(text: str, iter_backward: bool = False, max_dates: int = 0 ) -> Iterator[date]:
        The main general-purpose parse method. Takes a text string, and yields
        datetime.date objects for each matched date expression from left to right, or
        right to left if iter_backward is set to True. If max_dates is specified and nonzero,
        only yields at most that many dates before halting.

    get_first(text:str) , get_last(text:str)->datetime.date
        Wrappers for extract_and_parse to get only the
        leftmost or rightmost expression, respectively



    """

    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    pass
