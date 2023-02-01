"""Constant definitions and pre-compilation of regex patterns"""
import functools
import re
from typing import Iterable

MONTH_SHORTNAMES = [
    "",
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]  # one-indexed so that numeric month value is the same as the index

WEEKDAY_SHORTNAMES = [
    "",
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
]  # one-indexed for symmetry with MONTH_SHORTNAMES[],
# and to line up with datetime.date.isoweekday()


compile_pattern = functools.partial(re.compile, flags=re.IGNORECASE)

TIME_INTERVAL_TYPES = {"day": 1, "week": 7, "month": 30, "year": 365}


NEGATIVE_INTERVAL_WORDS = ["before"]
POSITIVE_INTERVAL_WORDS = ["from", "after"]

NUMBER_WORDS = [
    "",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
]

# utility function to convert an iterable to a
# regex pattern string matching any element in the list
# returned as a string rather than re.Pattern to allow further recombination
def _iter_to_regex(input_list: Iterable) -> str:
    return "|".join([str(s) for s in input_list if s])


QUICK_DAY_NAMES = ["today", "tomorrow", "yesterday"]

WHITESPACE_BUF = r"(?:\s*)"
# make regex pattern strings
MONTHS_MATCH_REGEX = _iter_to_regex(MONTH_SHORTNAMES)

# special corner case: since month and monday are confusable
WEEKDAY_MATCH_REGEX = "mon(day|\b)" + _iter_to_regex(WEEKDAY_SHORTNAMES[1:])


TIME_INTERVAL_REGEX = _iter_to_regex(TIME_INTERVAL_TYPES)
NUMBER_WORDS_REGEX = _iter_to_regex(NUMBER_WORDS)
QUICK_DAYS_REGEX = _iter_to_regex(QUICK_DAY_NAMES)

INTERVAL_PREPOSITION_REGEX = (
    _iter_to_regex(POSITIVE_INTERVAL_WORDS)
    + "|"
    + _iter_to_regex(NEGATIVE_INTERVAL_WORDS)
)


# compile_pattern patterns
# of the form "oct 20" "october 20" "10-20-2023
MDY_DATE_PATTERN = compile_pattern(
    WHITESPACE_BUF
    + r"(?P<month>"
    + MONTHS_MATCH_REGEX
    + r"|\d+)[^\d\n]+?(?P<day>\d{1,2})(?P<year>[^\d\n]+\d{4})?"
    + WHITESPACE_BUF
)

# phrases of the form "a week from"
RELATIVE_INTERVAL_PATTERN = compile_pattern(
    WHITESPACE_BUF
    + r"(?P<time_unit_count>a\s*|"
    + NUMBER_WORDS_REGEX
    + r")?\s*(?P<time_interval_name>"
    + TIME_INTERVAL_REGEX
    + r")\w*[^\n\d\w]*(?P<preposition>"
    + INTERVAL_PREPOSITION_REGEX
    + ")"
    + WHITESPACE_BUF
)

# phrases of the form "in ten days", "in two weeks"
IN_N_INTERVALS_PATTERN = compile_pattern(
    WHITESPACE_BUF
    + r"in[^\n\d\w](?P<days_number>\w+|a)[^\n\d\w](?P<time_interval_name>"
    + TIME_INTERVAL_REGEX
    + r")\w*?"
    + WHITESPACE_BUF
)

# phrases of the form "this sunday", "next wednesday"
RELATIVE_WEEKDAY_PATTERN = compile_pattern(
    WHITESPACE_BUF
    + r"(?P<specifier>this|next|last)?[^\n\d\w]*(?P<weekday_name>"
    + WEEKDAY_MATCH_REGEX
    + ")"
    + WHITESPACE_BUF
)

QUICK_DAYS_PATTERN = compile_pattern(
    WHITESPACE_BUF + r"(?P<quick_dayname>" + QUICK_DAYS_REGEX + ")" + WHITESPACE_BUF
)
