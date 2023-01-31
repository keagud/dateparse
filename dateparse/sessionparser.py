"""
Defines the API for the main operations exposed by the Dateparse package,
via the DateParser class.
"""

from datetime import date
from typing import Iterator

from .dateparser import DateParser


class DateParserSession(DateParser):

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

    iter_dates(text: str, iter_backward: bool = False) -> Iterator[date]:
        The main general-purpose parse method. Takes a text string, and yields
        date objects for each matched date expression from left to right, or
        right to left if iter_backward is set to True.

    get_first(text:str) , get_last(text:str)->date
        Wrappers for iter_dates to get only the
        leftmost or rightmost expression, respectively

    iter_dates_span(text:str) -> Iterator[tuple[date, int, int]]
    get_first_span, get_last_span -> tuple[date, int, int]
        These all take the same parameters as iter_dates, get_first and get_last, respectively.
        The only difference is that the span of the matched expression within the input text is
        returned as well. The returned date object is a NamedTuple with fields (date, start, end)
        accessible by direct reference or unpacking

    """

    def __init__(
        self,
        current_date: date | None = None,
        named_days: dict[str, str] | None = None,
        allow_past: bool = False,
    ) -> None:

        super().__init__()

        self.current_date = current_date if current_date is not None else date.today()

        self.named_days = self.default_named_days

        self.allow_past = allow_past

        if named_days is not None:
            self.named_days.update(named_days)

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def get_dates_list():
        pass
