from re import Match
from datetime import date, time
from datetime import timedelta

from itertools import chain
from functools import wraps
from typing import Callable

from .regex_utils import TIME_INTERVAL_TYPES
from .regex_utils import NEGATIVE_INTERVAL_WORDS, POSITIVE_INTERVAL_WORDS
from .regex_utils import WEEKDAY_SHORTNAMES
from .regex_utils import MONTH_SHORTNAMES

from .regex_utils import MDY_DATE_PATTERN
from .regex_utils import IN_N_INTERVALS_PATTERN
from .regex_utils import RELATIVE_WEEKDAY_PATTERN
from .regex_utils import RELATIVE_INTERVAL_PATTERN

from .date_classes import DateExpression, DateMatch


def match_to_dict(obj: DateMatch | dict[str, str]) -> dict[str, str]:
    if isinstance(obj, DateMatch):
        return obj.match_groups
    return obj


def mdy_parse(date_match: dict[str, str] | DateMatch, base_date: date) -> date:

    date_match = match_to_dict(date_match)

    month_str: str = date_match["month"]
    day_str: str = date_match["day"]

    if not month_str.isnumeric():
        month = MONTH_SHORTNAMES.index(month_str)
    else:
        month = int(month_str)

    day = int(day_str)

    year = int(date_match["year"]) if date_match["year"] else base_date.year

    return date(year, month, day)


def relative_interval_parse(
    date_match: dict[str, str] | DateMatch, base_date: date
) -> date:

    date_match = match_to_dict(date_match)

    unit_count = int(date_match["time_unit_count"])
    interval_name_str = date_match["time_interval_name"]
    preposition = date_match["preposition"]
    days_offset = timedelta(days=unit_count * TIME_INTERVAL_TYPES[interval_name_str])

    if preposition in NEGATIVE_INTERVAL_WORDS:
        days_offset *= -1

    return base_date + days_offset


def n_intervals_parse(date_match: DateMatch | dict[str, str], base_date: date) -> date:

    date_match = match_to_dict(date_match)

    days_num = int(date_match["days_number"])
    interval_name_str = date_match["time_interval_name"]

    days_offset = timedelta(days=TIME_INTERVAL_TYPES[interval_name_str] * days_num)

    return base_date + days_offset


def relative_weekday_parse(
    date_match: DateMatch | dict[str, str], base_date: date
) -> date:
    date_match = match_to_dict(date_match)

    specifier = date_match["specifier"]
    weekday_str = date_match["weekday_name"]

    weekday_num: int = WEEKDAY_SHORTNAMES.index(weekday_str)

    days_delta = weekday_num - base_date.isoweekday()

    # TODO refactor this to be less bad
    if days_delta <= 0:
        days_delta += 7

    if days_delta < 7 and specifier == "next":
        days_delta += 7

    return base_date + timedelta(days=days_delta)


date_expressions = (
    DateExpression(pattern=MDY_DATE_PATTERN, parse_func=mdy_parse),
    DateExpression(
        pattern=RELATIVE_INTERVAL_PATTERN, parse_func=relative_interval_parse
    ),
    DateExpression(pattern=IN_N_INTERVALS_PATTERN, parse_func=n_intervals_parse),
    DateExpression(pattern=RELATIVE_WEEKDAY_PATTERN, parse_func=relative_weekday_parse),
)
