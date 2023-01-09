"""
Defines the API for the main operations exposed by the Dateparse package,
via the DateParser class.
"""

from datetime import date
from pprint import pformat
from typing import Iterable
from typing import Iterator
from calendar import monthrange
from collections import namedtuple
import sys
import logging

from ._parse_util import DateMatch
from ._parse_util import DateGroups
from ._parse_util import AbsoluteDateExpression
from ._parse_util import DateValues
from ._parse_util import date_expressions as defined_date_exprs


if len(sys.argv) > 1 and sys.argv[1].lower() == "--debug":
    logging.basicConfig(level=logging.DEBUG)

DateInfoTuple = namedtuple("DateInfoTuple", ["date", "start", "end"])


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

    def __init__(
        self,
        current_date: date | None = None,
        named_days: dict[str, str] | None = None,
        allow_past: bool = False,
    ) -> None:
        """
        Constructor for a DateParser.

        Params:
            current_date: date | None = None
                Sets the self.current_date attribute.
                If None (default), self.current_date is set to datetime.date.today()
            named_days: dict[str,str] | None = None
                User-defined named day aliases, which are added to the predefined defaults
                to form the self.named_days attribute.
            allow_past: bool = False
                If true (default), will correct outputted dates to the next valid occurrence
                after self.current_date, if they would fall before it
        """

        self.date_expressions = defined_date_exprs

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

    def group_match_tokens(self, text: str) -> DateGroups:
        """Group date expressions that combine to form a single date into a DateGroups object"""
        text = self.sub_named_days(text)
        return DateGroups(text, self.date_expressions)

    def parse_date_match(self, date_match: DateMatch) -> date | DateValues:
        """
        Wrapper to call the to_date() method on the given DateMatch object and return the result
        Result is either a datetime.date or DateValues object.
        """
        return date_match.to_date(self.current_date)

    def parse_tokens(self, match_iter: Iterable[DateMatch]) -> date:

        """
        Takes an iterable consisting of an AbsoluteDateExpression
        preceded by any number of DeltaDateExpressions

        Returns the date object representing the absolute expression + the sum of all deltas
        Any deltas that come after the absolute expression are ignored.
        """

        logging.debug(
            "\nENTERING PARSE_TOKENS WITH PARAMS: %s",
            pformat([m.content for m in match_iter]),
        )

        offset: list[DateValues] = []
        anchor_date: date | None = None

        for match in match_iter:

            logging.debug("\ttoken: %s", match.content)
            if isinstance(match.expression, AbsoluteDateExpression):
                logging.debug("\tAnchor date: %s", match.content)
                anchor_date = match.to_date(self.current_date)
                break

            offset.append(match.to_date(self.current_date))

            logging.debug(
                "\tDelta: %s as %s",
                pformat(match.content),
                str(match.to_date(self.current_date)),
            )

        if anchor_date is None:
            raise ValueError(
                f"Unable to parse as a date: {' '.join([c.content for c in match_iter])}"
            )

        # determine the total amount of time to offset the anchor date
        # by summing all deltas
        total_offsets = {"day": 0, "month": 0, "year": 0}

        for delta in offset:
            for interval, count in delta.to_dict().items():
                if not interval in total_offsets:
                    continue
                total_offsets[interval] += count

        # add the delta sum to anchor for the final result
        date_vals = DateValues(
            srcdict={
                "day": anchor_date.day + total_offsets["day"],
                "month": anchor_date.month + total_offsets["month"],
                "year": anchor_date.year + total_offsets["year"],
            }
        )

        # If the new sum of months is less than 1 or greater than 12,
        # allow for wrapping into the previous or next year

        if not 0 < date_vals.month < 13:
            month_val = date_vals.month
            adjusted_month = ((month_val - 1) % 12) + 1
            year_offset = (month_val - 1) // 12

            date_vals.month = adjusted_month
            date_vals.year += year_offset

        _, maxdays = monthrange(date_vals.year, date_vals.month)

        if date_vals.day > maxdays:

            date_vals.month += date_vals.day // maxdays
            date_vals.day = date_vals.day % maxdays

        parsed_date = date(**date_vals.to_dict())

        if parsed_date < self.current_date and not self.allow_past:
            parsed_date = parsed_date.replace(year=self.current_date.year + 1)

        return parsed_date

    def extract_dates_info(
        self, text: str, iter_backward: bool = False, max_dates: int = 0
    ) -> Iterator[DateInfoTuple]:
        """
        Main wrapper method for extracting date expressions from a string.
        Output: Iterator over datetime.date objects
        Params:
        _______

            text:str
                The input text to be scanned through.
                If no known date format patterns are matched, raises a ValueError

            iter_backward = False:
                If set to True, iteration starts at the right and moves leftward (default: False)

            max_dates = 0
                The maximum number of dates to parse before halting.
                If zero (the default), will continue as long as the string contains matches.
        """

        groups = self.group_match_tokens(text).get_groups()

        if not groups[0]:
            return None
            
        if iter_backward:
            groups.reverse()

        for index, tokens in enumerate(groups, start=1):
            group_start = min([t.start_index for t in tokens])
            group_end = max([t.end_index for t in tokens])
            yield DateInfoTuple(self.parse_tokens(tokens), group_start, group_end)

            if 0 < max_dates <= index:
                break

    def extract_and_parse(
        self, text: str, iter_backward: bool = False, max_dates: int = 0
    ) -> Iterator[date]:
        """Wraps extract_dates_info, taking the same params, but yields only the date."""
        gen = self.extract_dates_info(
            text, iter_backward=iter_backward, max_dates=max_dates
        )
        for date_info in gen:
            yield date_info.date

    def get_first_info(self, text: str) -> DateInfoTuple:
        """Gets full info (date object + start and end indices) for first date in a string"""
        gen = self.extract_dates_info(text, max_dates=1)
        return next(gen)

    def get_last_info(self, text: str) -> DateInfoTuple:
        """Gets full info (date object + start and end indices) for last date in a string"""
        gen = self.extract_dates_info(text, max_dates=1, iter_backward=True)
        return next(gen)

    def get_first(self, text: str) -> date:
        """Gets the first (leftmost) date in a string"""
        gen = self.extract_and_parse(text, max_dates=1)
        return next(gen)

    def get_last(self, text: str) -> date:
        """Gets the last (rightmost) date in a string"""
        gen = self.extract_and_parse(text, max_dates=1, iter_backward=True)
        return next(gen)
