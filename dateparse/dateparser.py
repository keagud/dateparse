"""
Defines the API for the main operations exposed by the Dateparse package,
via the DateParser class.
"""

from datetime import date
from typing import Iterator
from typing import NamedTuple


from .parser.date_processor import DateProcessor
from .parser.date_processor import DateResult


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

    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(
        self,
        current_date: date | None = None,
        named_days: dict[str, str] | None = None,
        allow_past: bool = False,
    ) -> None:

        self.current_date = current_date if current_date is not None else date.today()

        self.named_days = self.default_named_days

        self.allow_past = allow_past

        if named_days is not None:
            self.named_days.update(named_days)

    def sub_named_days(self, text: str):

        """
        Substitutes all substrings in the input for their corresponding value in self.named_days.
        Returns the processed string.
        """
        text = text.lower()

        for day_name, repl_str in self.named_days.items():
            if day_name in text:
                text = text.replace(day_name, repl_str)
        return text

    def iter_dates(
        self, text: str, iter_backward: bool = False
    ) -> Iterator[date | None]:

        return DateProcessor.iter_dates(
            text, self.current_date, from_right=iter_backward
        )

    def get_first(self, text: str) -> date | None:
        return next(self.iter_dates(text))

    def get_last(self, text: str) -> date | None:
        return next(self.iter_dates(text, iter_backward=True))

    def iter_dates_span(
        self, text: str, iter_backward: bool = False
    ) -> Iterator[DateResult | None]:

        return DateProcessor.iter_dates_span(
            text, self.current_date, from_right=iter_backward
        )

    def get_first_span(self, text: str) -> DateResult | None:
        return next(self.iter_dates_span(text))

    def get_last_span(self, text: str) -> DateResult | None:
        return next(self.iter_dates_span(text, iter_backward=True))
