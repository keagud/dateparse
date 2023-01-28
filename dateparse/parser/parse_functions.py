from typing import Callable, NamedTuple
from re import Pattern, Match
from datetime import date, timedelta

from abc import ABCMeta

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


absolute_patterns = [
    MDY_DATE_PATTERN,
    IN_N_INTERVALS_PATTERN,
    RELATIVE_WEEKDAY_PATTERN,
    QUICK_DAYS_PATTERN,
]
relative_patterns = [RELATIVE_INTERVAL_PATTERN]


class DateTuple(NamedTuple):
    pattern: Pattern
    fields: dict
    content: str
    start: int
    end: int


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


def mdy_parse(date_tuple: DateTuple, base_date: date) -> date:
    """Parse function for expressions like "October 10." """

    date_fields = date_tuple.fields

    month_str: str = date_fields["month"]
    day_str: str = date_fields["day"]

    if not month_str.isnumeric():
        month = MONTH_SHORTNAMES.index(month_str)
    else:
        month = int(month_str)

    day = int(day_str)

    year = int(date_fields["year"]) if "year" in date_fields else base_date.year

    return date(year, month, day)


def n_intervals_parse(date_tuple: DateTuple, base_date: date) -> date:
    """Parse function for expressions like "In ten days." """

    date_fields = date_tuple.fields

    days_num = normalize_number(date_fields["days_number"])
    interval_name_str = date_fields["time_interval_name"]

    days_offset = timedelta(days=TIME_INTERVAL_TYPES[interval_name_str] * days_num)

    return base_date + days_offset


def relative_weekday_parse(date_tuple: DateTuple, base_date: date) -> date:
    """Parse function for expressions like "this Wednesday" """

    date_fields = date_tuple.fields
    specifier = date_fields.get("specifier", "")
    weekday_str = date_fields["weekday_name"]

    weekday_num: int = WEEKDAY_SHORTNAMES.index(weekday_str)

    days_delta = weekday_num - base_date.isoweekday()

    if days_delta <= 0:
        days_delta += 7

    if days_delta < 7 and specifier == "next":
        days_delta += 7
    # TODO past dates are not accounted for here

    return base_date + timedelta(days=days_delta)


# TODO
def relative_interval_parse(
    date_tuple: DateTuple, base_date: date
) -> timedelta:  # type: ignore

    """Parse function for expressions like "Four days after", "a week before" """

    date_fields = date_tuple.fields
    units_count = normalize_number(date_fields.get("time_unit_count", "one"))
    interval_name_str = date_fields["time_interval_name"]
    preposition = date_fields["preposition"]

    if preposition in NEGATIVE_INTERVAL_WORDS:
        units_count *= -1

    if interval_name_str == "week":
        interval_name_str = "day"
        units_count *= 7

    # TODO
    # return DateValues(**{interval_name_str: units_count})


def quick_day_parse(date_tuple: DateTuple, base_date: date) -> date:

    """Parse function for "today", "tomorrow", "yesterday" """
    date_fields = date_tuple.fields

    offset = timedelta(
        days={"today": 0, "tomorrow": 1, "yesterday": -1}[date_fields["quick_dayname"]]
    )

    return base_date + offset


absolute_functions_index: dict[Pattern, Callable[[DateTuple, date], date]] = {
    MDY_DATE_PATTERN: mdy_parse,
    IN_N_INTERVALS_PATTERN: n_intervals_parse,
    RELATIVE_WEEKDAY_PATTERN: relative_weekday_parse,
    QUICK_DAYS_PATTERN: quick_day_parse,
}

relative_functions_index = {RELATIVE_INTERVAL_PATTERN: relative_interval_parse}
