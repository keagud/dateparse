from typing import Callable, NamedTuple
from typing import Any
from re import Pattern, Match
from datetime import date, timedelta
from calendar import monthrange
from calendar import isleap
from itertools import repeat
import datetime

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
    """Container for data about a matched date expression"""

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

    date_fields:dict [str, Any] = date_tuple.fields

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


def quick_day_parse(date_tuple: DateTuple, base_date: date) -> date:

    """Parse function for "today", "tomorrow", "yesterday" """
    date_fields = date_tuple.fields

    offset = timedelta(
        days={"today": 0, "tomorrow": 1, "yesterday": -1}[date_fields["quick_dayname"]]
    )

    return base_date + offset


def months_iter(d: date, forward: bool = True):
    class MonthInfo(NamedTuple):
        days: int
        month_num: int
        year: int

    start_month = d.month
    start_year = d.year

    month_range_start = 1 if forward else 12
    month_range_end = 13 if forward else 0
    step = 1 if forward else -1

    def pack_month_info(y: int, m: int):
        _, month_days = monthrange(y, m)
        return MonthInfo(month_days, m, y)

    for m, y in zip(range(start_month, month_range_end, step), repeat(start_year)):
        yield pack_month_info(y, m)

    month_year = start_year + step
    while datetime.MINYEAR < month_year < datetime.MAXYEAR:
        for m, y in zip(
            range(month_range_start, month_range_end, step), repeat(month_year)
        ):
            yield pack_month_info(y, m)

        month_year += step


def month_delta(input_date: date, months_count: int, forward: bool = True):
    """
    Get a timedelta for the span months_count after input_date,
    or before if forward is False.
    """
    total_days: int = 0

    delta_iter = months_iter(input_date, forward=forward)
    next(delta_iter)
    for _ in range(months_count):
        total_days += next(delta_iter).days

    if not forward:
        total_days *= -1

    return timedelta(days=total_days)


def year_delta(input_date: date, years_count: int, forward: bool = True) -> timedelta:
    """
    Get a timedelta of years_count years after input_date,
    or before if forward is False.
    Accounts for leap years.
    """

    start_year = input_date.year
    start_month = input_date.month
    start_day = input_date.day

    if not forward:
        years_count *= -1

    end_year = start_year + years_count

    # look before you leap!
    if start_month == 2 and start_day == 29:
        if not isleap(end_year):
            start_day -= 1

    end_date = date(year=end_year, month=start_month, day=start_day)

    return end_date - input_date


def relative_interval_parse(date_tuple: DateTuple, base_date: date) -> timedelta:

    import pdb; pdb.set_trace()
    """Parse function for expressions like "Four days after", "a week before" """

    date_fields = date_tuple.fields
    units_count = normalize_number(date_fields.get("time_unit_count", "one"))
    interval_name_str = date_fields["time_interval_name"]
    preposition = date_fields["preposition"]

    negative_interval = preposition in NEGATIVE_INTERVAL_WORDS

    if interval_name_str == "month":
        return month_delta(base_date, units_count, forward=negative_interval)

    if interval_name_str == "year":
        return year_delta(base_date, units_count, forward=negative_interval)

    if interval_name_str == "week":
        interval_name_str = "day"
        units_count *= 7

    if negative_interval:
        units_count *= -1

    return timedelta(days=units_count)


absolute_functions_index: dict[Pattern, Callable[[DateTuple, date], date]] = {
    MDY_DATE_PATTERN: mdy_parse,
    IN_N_INTERVALS_PATTERN: n_intervals_parse,
    RELATIVE_WEEKDAY_PATTERN: relative_weekday_parse,
    QUICK_DAYS_PATTERN: quick_day_parse,
}

relative_functions_index = {RELATIVE_INTERVAL_PATTERN: relative_interval_parse}
