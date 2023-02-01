"""Processing utilities for """
import datetime
import re
from calendar import isleap, monthrange
from itertools import repeat
from typing import Any, Callable, NamedTuple

from .regex_utils import (
    IN_N_INTERVALS_PATTERN,
    MDY_DATE_PATTERN,
    MONTH_SHORTNAMES,
    NEGATIVE_INTERVAL_WORDS,
    NUMBER_WORDS,
    QUICK_DAYS_PATTERN,
    RELATIVE_INTERVAL_PATTERN,
    RELATIVE_WEEKDAY_PATTERN,
    TIME_INTERVAL_TYPES,
    WEEKDAY_SHORTNAMES,
)


class DateTuple(NamedTuple):
    """Container for data about a matched date expression."""

    pattern: re.Pattern
    fields: dict
    content: str
    start: int
    end: int

    date: datetime.date | datetime.timedelta | None = None


class DateResult(NamedTuple):
    """Container for a processed date."""

    date: datetime.date
    start: int
    end: int
    content: str


class ExpressionGrouping(NamedTuple):
    """Holds a set of DateTuples which can be combined into a single expression."""

    anchor: DateTuple
    deltas: list[DateTuple]


class _MonthInfo(NamedTuple):
    days: int
    month_num: int
    year: int


absolute_patterns = [
    MDY_DATE_PATTERN,
    IN_N_INTERVALS_PATTERN,
    RELATIVE_WEEKDAY_PATTERN,
    QUICK_DAYS_PATTERN,
]
relative_patterns = [RELATIVE_INTERVAL_PATTERN]


def _normalize_number(number_term: str | None) -> int:
    """Converts a number word as a string to an int, raises ValueError if not a number."""

    if number_term is None:
        return 1

    number_term = number_term.strip().lower()

    if number_term in {"a", "one", "the"}:
        return 1

    if number_term.isnumeric():
        return int(number_term)

    if number_term and number_term in NUMBER_WORDS:
        return NUMBER_WORDS.index(number_term)

    raise ValueError(
        f"Format required a number but '{number_term}' could not be converted to one"
    )


def _mdy_parse(date_tuple: DateTuple, base_date: datetime.date) -> datetime.date:
    """Parse function for expressions like "October 10." """

    date_fields: dict[str, Any] = date_tuple.fields

    month_str: str = date_fields["month"]
    day_str: str = date_fields["day"]

    if not month_str.isnumeric():
        month = MONTH_SHORTNAMES.index(month_str.lower())
    else:
        month = int(month_str)

    day = int(day_str)

    year = base_date.year
    if "year" in date_fields and date_fields["year"] is not None:
        year = int(date_fields["year"])

    return datetime.date(year, month, day)


def _n_intervals_parse(
    date_tuple: DateTuple, base_date: datetime.date
) -> datetime.date:
    """Parse function for expressions like "In ten days." """

    date_fields = date_tuple.fields

    days_num = _normalize_number(date_fields["days_number"])
    interval_name_str = date_fields["time_interval_name"]

    days_offset = datetime.timedelta(
        days=TIME_INTERVAL_TYPES[interval_name_str] * days_num
    )

    return base_date + days_offset


def _relative_weekday_parse(
    date_tuple: DateTuple, base_date: datetime.date
) -> datetime.date:
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

    return base_date + datetime.timedelta(days=days_delta)


def _quick_day_parse(date_tuple: DateTuple, base_date: datetime.date) -> datetime.date:

    """Parse function for "today", "tomorrow", "yesterday" """
    date_fields = date_tuple.fields

    offset = datetime.timedelta(
        days={"today": 0, "tomorrow": 1, "yesterday": -1}[date_fields["quick_dayname"]]
    )

    return base_date + offset


def _pack_month_info(year_value: int, month_value: int):
    _, month_days = monthrange(year_value, month_value)
    return _MonthInfo(month_days, month_value, year_value)


def _months_iter(start_date: datetime.date, backward: bool = False):
    """Iterate by month forward or backward from start_date"""
    start_month = start_date.month
    start_year = start_date.year

    month_range_start = 1 if not backward else 12
    month_range_end = 13 if not backward else 0
    step = 1 if not backward else -1

    for month, year in zip(
        repeat(start_year), range(start_month, month_range_end, step)
    ):
        yield _pack_month_info(month, year)

    month_year = start_year + step

    while datetime.MINYEAR < month_year < datetime.MAXYEAR:
        for month, year in zip(
            repeat(month_year), range(month_range_start, month_range_end, step)
        ):
            yield _pack_month_info(month, year)

        month_year += step


def _month_delta(input_date: datetime.date, months_count: int, backward: bool = False):
    """
    Get a timedelta for the span months_count after input_date,
    or before if forward is False.
    """

    delta_list = list(_months_iter(input_date, backward=backward))
    total_days = sum(month.days for month in delta_list[:months_count])

    if backward:
        total_days *= -1

    return datetime.timedelta(days=total_days)


def _year_delta(
    input_date: datetime.date, years_count: int, backward: bool = False
) -> datetime.timedelta:
    """
    Get a timedelta of years_count years after input_date,
    or before if forward is False.
    Accounts for leap years.
    """

    start_year = input_date.year
    start_month = input_date.month
    start_day = input_date.day

    if backward:
        years_count *= -1

    end_year = start_year + years_count

    # look before you leap!
    if start_month == 2 and start_day == 29:
        if not isleap(end_year):
            start_day -= 1

    end_date = datetime.date(year=end_year, month=start_month, day=start_day)

    return end_date - input_date


def _relative_interval_parse(
    date_tuple: DateTuple, base_date: datetime.date
) -> datetime.timedelta:
    """Parse function for expressions like "Four days after", "a week before" """

    date_fields = date_tuple.fields
    units_count = _normalize_number(date_fields.get("time_unit_count", "one"))
    interval_name_str = date_fields["time_interval_name"]
    preposition = date_fields["preposition"]

    negative_interval = preposition in NEGATIVE_INTERVAL_WORDS

    if interval_name_str == "month":
        return _month_delta(base_date, units_count, backward=negative_interval)

    if interval_name_str == "year":
        return _year_delta(base_date, units_count, backward=negative_interval)

    if interval_name_str == "week":
        interval_name_str = "day"
        units_count *= 7

    if negative_interval:
        units_count *= -1

    return datetime.timedelta(days=units_count)


absolute_functions_index: dict[
    re.Pattern, Callable[[DateTuple, datetime.date], datetime.date]
] = {
    MDY_DATE_PATTERN: _mdy_parse,
    IN_N_INTERVALS_PATTERN: _n_intervals_parse,
    RELATIVE_WEEKDAY_PATTERN: _relative_weekday_parse,
    QUICK_DAYS_PATTERN: _quick_day_parse,
}

relative_functions_index = {RELATIVE_INTERVAL_PATTERN: _relative_interval_parse}
