""" Definitions for classes representing different types of date expressions and related data """
from re import Pattern
from re import Match
from re import finditer

import logging
from pprint import pformat

from typing import Iterable
from typing import Callable

from datetime import date
from datetime import timedelta

from dataclasses import dataclass


from .regex_utils import TIME_INTERVAL_TYPES
from .regex_utils import NEGATIVE_INTERVAL_WORDS
from .regex_utils import WEEKDAY_SHORTNAMES
from .regex_utils import MONTH_SHORTNAMES

from .regex_utils import MDY_DATE_PATTERN
from .regex_utils import IN_N_INTERVALS_PATTERN
from .regex_utils import RELATIVE_WEEKDAY_PATTERN
from .regex_utils import RELATIVE_INTERVAL_PATTERN
from .regex_utils import QUICK_DAYS_PATTERN

from .regex_utils import NUMBER_WORDS


class DateValues:
    """
    Class to store date parameters in a more flexible (mutible) way than a date object

    day, week, month, and year params can be specified individually to allow an isinstance
    to express a delta or interval, or a dict of a day month and year (kwargs of a datetime.date
    constructor) can be passed instead.

    to_dict(self): returns a dict of that same form, can be used as **kwargs for a date object
    """

    def __init__(
        self,
        day: int = 0,
        week: int = 0,
        month: int = 0,
        year: int = 0,
        srcdict: dict[str, int] | None = None,
    ) -> None:

        if srcdict is not None:
            self.day = srcdict.get("day", 0)
            self.month = srcdict.get("month", 0)
            self.year = srcdict.get("year", 0)

            return

        if week != 0:
            self.day = week * 7

        self.day = day
        self.month = month
        self.year = year

    def to_dict(self):
        """Returns day, month, and year values in a dict."""
        return {"day": self.day, "month": self.month, "year": self.year}


@dataclass(frozen=True, kw_only=True)
class DateExpression:
    """
    Superclass for any kind of date expression
    parse_func: the function to be called to convert this expression to a date
    pattern: the original re.Pattern associated with the expression.
    """

    parse_func: Callable
    pattern: Pattern


class AbsoluteDateExpression(DateExpression):
    """DateExpression subclass for expressions that form an independent date"""

    parse_func: Callable[..., date]


class DeltaDateExpression(DateExpression):
    """DateExpression subclass for expressions that act as modifiers to an absolute date"""

    parse_func: Callable[..., DateValues]


class DateMatch:
    """
    Class representing an occurrence of a DateExpression found in the text

    Members:
        expression: the DateExpression object matched against
        start_index, end_index: int indices of the start and end of the matched
            substring within the text
        content: the substring that was matched
        base_match: the re.Match object that was originally matched against
        match_groups: dict of the named groups of base_match
    """

    __slots__ = (
        "expression",
        "start_index",
        "end_index",
        "content",
        "base_match",
        "match_groups",
    )

    def __init__(self, expression: DateExpression, match_obj: Match) -> None:

        self.expression: DateExpression = expression
        self.start_index: int = match_obj.start()
        self.end_index: int = match_obj.end()
        self.content: str = match_obj.group().strip()
        self.base_match: Match[str] = match_obj

        self.match_groups: dict = match_obj.groupdict()

        logging.debug(
            "Created new DateMatch: \n\tPattern: %s" "\n\tSpan: %d - %d\n\tContent: %s",
            self.expression.pattern,
            self.start_index,
            self.end_index,
            self.content,
        )

    def to_date(self, current_date: date):
        return self.expression.parse_func(self, current_date)


class DateGroups:
    def __init__(
        self,
        text: str,
        expressions: Iterable[DateExpression],
        consecutive: bool = True,
    ) -> None:
        self.text = text
        self.expressions = expressions
        self.reversed = reversed
        self.consecutive = consecutive

    def get_consecutive(self, matches_list: list[DateMatch]) -> list[list[DateMatch]]:
        """
        Given a list of DateMatch objects,
        groups them based on the segments that are consecutive within the original string.
        Returns a list of lists of DateMatch objects.
        """

        match_groups: list[list[DateMatch]] = []
        group: list[DateMatch] = []

        prev: DateMatch | None = None
        for match in matches_list:
            if prev is not None:
                # rule out matches fully contained within other matches
                if (
                    prev.start_index <= match.start_index
                    and prev.end_index >= match.end_index
                ):

                    continue
                start_diff = abs(match.start_index - prev.end_index)
                end_diff = abs(match.end_index - prev.start_index)

                if start_diff > 1 and end_diff > 1:
                    match_groups.append(group)
                    group = []

            group.append(match)
            prev = match
        match_groups.append(group)

        logging.debug(
            "Consecutive grouping: %s",
            pformat([[d.content for d in s] for s in match_groups]),
        )

        return match_groups

    def get_groups(self) -> list[list[DateMatch]]:
        """Extracts any expressions in self.text that match one of self.expressions"""

        all_matches: list[DateMatch] = []

        match_iterators = (
            (expr, finditer(expr.pattern, self.text)) for expr in self.expressions
        )

        for match_expr, match_iter in match_iterators:

            matches = [
                DateMatch(
                    expression=match_expr,
                    match_obj=match,
                )
                for match in match_iter
                if match
            ]

            all_matches.extend(matches)

        all_matches.sort(key=lambda x: x.start_index)

        return self.get_consecutive(all_matches)


def match_to_dict(obj: DateMatch | dict[str, str]) -> dict[str, str]:
    if isinstance(obj, DateMatch):
        return {
            k: v.lower().strip()
            for k, v in obj.match_groups.items()
            if k is not None and v is not None
        }

    return obj


def normalize_number(number_term: str) -> int:

    """Converts a number word as a string to an int, raises ValueError if not a number"""

    number_term = number_term.strip().lower()

    if number_term in ("a", "one", "the"):
        return 1

    if number_term.isnumeric():
        return int(number_term)

    if number_term and number_term in NUMBER_WORDS:
        return NUMBER_WORDS.index(number_term)

    raise ValueError(
        f"Format required a number but '{number_term}' could not be converted to one"
    )


def mdy_parse(date_match: dict[str, str] | DateMatch, base_date: date) -> date:
    """Parse function for expressions like "October 10." """

    date_match = match_to_dict(date_match)

    month_str: str = date_match["month"]
    day_str: str = date_match["day"]

    if not month_str.isnumeric():
        month = MONTH_SHORTNAMES.index(month_str)
    else:
        month = int(month_str)

    day = int(day_str)

    year = int(date_match["year"]) if "year" in date_match else base_date.year

    return date(year, month, day)


def n_intervals_parse(date_match: DateMatch | dict[str, str], base_date: date) -> date:
    """Parse function for expressions like "In ten days." """

    date_match = match_to_dict(date_match)

    days_num = normalize_number(date_match["days_number"])
    interval_name_str = date_match["time_interval_name"]

    days_offset = timedelta(days=TIME_INTERVAL_TYPES[interval_name_str] * days_num)

    return base_date + days_offset


def relative_weekday_parse(
    date_match: DateMatch | dict[str, str], base_date: date
) -> date:
    """Parse function for expressions like "this Wednesday" """
    date_match = match_to_dict(date_match)

    specifier = date_match.get("specifier", "")
    weekday_str = date_match["weekday_name"]

    weekday_num: int = WEEKDAY_SHORTNAMES.index(weekday_str)

    days_delta = weekday_num - base_date.isoweekday()

    # if
    if days_delta <= 0:
        days_delta += 7

    if days_delta < 7 and specifier == "next":
        days_delta += 7

    return base_date + timedelta(days=days_delta)


def relative_interval_parse(
    date_match: dict[str, str] | DateMatch, _: date
) -> DateValues:

    """Parse function for expressions like "Four days after", "a week before" """

    date_match = match_to_dict(date_match)
    units_count = normalize_number(date_match.get("time_unit_count", "one"))
    interval_name_str = date_match["time_interval_name"]
    preposition = date_match["preposition"]

    if preposition in NEGATIVE_INTERVAL_WORDS:
        units_count *= -1

    if interval_name_str == "week":
        interval_name_str = "day"
        units_count *= 7

    return DateValues(**{interval_name_str: units_count})


def quick_day_parse(date_match: dict[str, str] | DateMatch, base_date: date) -> date:

    """Parse function for "today", "tomorrow", "yesterday" """

    date_match = match_to_dict(date_match)

    offset = timedelta(
        days={"today": 0, "tomorrow": 1, "yesterday": -1}[date_match["quick_dayname"]]
    )

    return base_date + offset


# declare the DateExpression objects and wrap them in a tuple for easy imports and iteration
date_expressions = (
    AbsoluteDateExpression(pattern=MDY_DATE_PATTERN, parse_func=mdy_parse),
    AbsoluteDateExpression(
        pattern=IN_N_INTERVALS_PATTERN, parse_func=n_intervals_parse
    ),
    AbsoluteDateExpression(
        pattern=RELATIVE_WEEKDAY_PATTERN, parse_func=relative_weekday_parse
    ),
    AbsoluteDateExpression(pattern=QUICK_DAYS_PATTERN, parse_func=quick_day_parse),
    DeltaDateExpression(
        pattern=RELATIVE_INTERVAL_PATTERN,
        parse_func=relative_interval_parse,
    ),
)
