""" Defines the API for the main operations exposed by the Dateparse package, via the the DateParser class. """

__author__ = "keagud"
__contact__ = "keagud@protonmail.com"
__license__ = "GPL 3.0 or later"
__version__ = "0.9"


from datetime import date, timedelta
from pprint import pformat
from typing import Iterable
from typing import Iterator


import sys

import logging


from ._parse_util import DateMatch
from ._parse_util import DateGroups
from ._parse_util import AbsoluteDateExpression
from ._parse_util import DateDelta
from ._parse_util import date_expressions as defined_date_exprs


if len(sys.argv) > 1 and sys.argv[1].lower() == "--debug":
    logging.basicConfig(level=logging.DEBUG)


class DateParser:
    """
    The intended interface for converting a natural language date expression into a date
    (datetime.date) object.

    Attributes:
    ------------

    current_date: datetime.date
        The date to be used to determine how to parse expressions that require temporal context,
        e.g. "A week from this Sunday", "In four days"

        If not passed into the constructor, defaults to the current date (datetime.date.today()).

    named_days: dict[str,str]
        Aliases for date expressions; occurances of each key will be substituted for the corrisponding value before parsing begins.
        This allows for dates of personal importance to be named directly.
        e.g. {'my birthday': 'october 17'} will cause the string 'my birthday' to act as an alias for 'october 17'


    Methods:
    ___________

    __init__(current_date: datetime.date | None = None, named_days: dict[str,str] | None = None,) -> None:
        Constructor for creating a new DateParser object.

    sub_named_days(text:str) -> str:
        Substitutes each occurance of a defined alias from named_days (both passed in at init time or included from the defaults
        list) with its corrisponding replacement string.

    group_match_tokens(text:str) -> DateGroups:
        Locates expressions in the text that match a known date pattern, and groups consecutive expressions together
        as a DateGroups object.

    parse_date_match(date_match: DateMatch) -> datetime.date | DateDelta
        For the given DateMatch object, call its to_date() method and return the result.
        If the DateMatch represents a modifier rather than an absolute date, returns as a DateDelta,
        otherwise returns a datetime.date


    parse_tokens(match_iter: Iterable[DateMatch]) -> date:
        Returns the date created from summating DateMatch objects referring to DeltaDateExpressions (e.g. 'a week from') from the
        match_iter iterable, until a an AbsoluteDateExpression (an expression than can unambiguously be converted to a date, potentially
        using the current date as a reference) is encountered.

        In practice, this means parse_tokens will take an iterable like ['a week from', 'the day after', 'Tuesday', 'foo'] and combine
        the contents up to and including 'Tuesday', which it returns as a datetime.date

    extract_and_parse(text: str, iter_backward: bool = False, max_dates: int = 0 ) -> Iterator[date]:
        The main general-purpose parse method. Takes a text string, and yields datetime.date objects for each matched date expression 
        from left to right, or right to left if iter_backward is set to True. If max_dates is specified and nonzero, only yields at most that
        many dates before halting.

    get_first(text:str) , get_last(text:str)->datetime.date
        Wrappers for extract_and_parse to get only the leftmost or rightmost expression, respectively



    """

    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(
        self, current_date: date | None = None, named_days: dict[str, str] | None = None
    ) -> None:

        self.date_expressions = defined_date_exprs

        self.current_date = current_date if current_date is not None else date.today()

        self.named_days = self.default_named_days

        if named_days is not None:
            self.named_days.update(named_days)

    def sub_named_days(self, text: str):

        text = text.lower()

        for day_name, repl_str in self.named_days.items():
            if day_name in text:
                text = text.replace(day_name, repl_str)
        return text

    def group_match_tokens(self, text: str) -> DateGroups:
        text = self.sub_named_days(text)
        return DateGroups(text, self.date_expressions)

    def parse_date_match(self, date_match: DateMatch) -> date | DateDelta:
        return date_match.to_date(self.current_date)

    def parse_tokens(self, match_iter: Iterable[DateMatch]) -> date:

        """
        Takes an iterable consisting of an AbsoluteDateExpression
        preceeded by any number of DeltaDateExpressions

        Returns the date object representing the absolute expression + the sum of all deltas
        Any deltas that come after the absolute expression are ignored.
        """

        logging.debug(
            "\nENTERING PARSE_TOKENS WITH PARAMS: %s",
            pformat([m.content for m in match_iter]),
        )

        offset: list[DateDelta] = []
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
            for interval, count in vars(delta).items():
                if not interval in total_offsets:
                    continue
                total_offsets[interval] += count

        # add the delta sum to anchor for the final result

        parsed_date_values = {
            "day": anchor_date.day + total_offsets["day"],
            "month": anchor_date.month + total_offsets["month"],
            "year": anchor_date.year + total_offsets["year"],
        }

        # If the new sum of months is less than 1 or greater than 12,
        # allow for wrapping into the previous or next year

        if not 0 < parsed_date_values["month"] < 13:
            month_val = parsed_date_values["month"]
            adjusted_month = ((month_val - 1) % 12) + 1
            year_offset = (month_val - 1) // 12

            parsed_date_values["month"] = adjusted_month
            parsed_date_values["year"] += year_offset

        parsed_date = date(**parsed_date_values)

        if parsed_date < self.current_date:
            parsed_date = parsed_date.replace(year=self.current_date.year + 1)

        return parsed_date

    def extract_and_parse(
        self, text: str, iter_backward: bool = False, max_dates: int = 0
    ) -> Iterator[date]:
        """
        Main wrapper method for converting a complex string expression to a datetime.date object.
        Input: text as a string
        Output: datetime.date object
        If no known date format patterns are matched, raises a ValueError
        """

        groups = self.group_match_tokens(text).get_groups()

        if not groups:
            raise ValueError(
                f"Could not match against any date expression types: {text}"
            )

        if iter_backward:
            groups.reverse()

        for index, tokens in enumerate(groups, start=1):
            yield self.parse_tokens(tokens)

            if 0 < max_dates <= index:
                break

    def get_first(self, text: str) -> date:
        gen = self.extract_and_parse(text, max_dates=1)
        return next(gen)

    def get_last(self, text: str) -> date:
        gen = self.extract_and_parse(text, max_dates=1, iter_backward=True)
        return next(gen)
