import re
from re import Pattern
from collections import namedtuple
from dataclasses import dataclass

from datetime import date
from typing import Iterable


Date_Formats = {"ISO": "%Y-%m-%d"}

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


TIME_INTERVAL_TYPES = {
    "day": 1,
    "week": 7,
    # TODO there's not always 30 days in a month - address this
    "month": 30,
    "year": 365,
}


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
def iter_to_regex(input_list: Iterable) -> str:
    return "|".join([str(s) for s in input_list if s])


whitespace_buffer = r"(?:\s*)"
# make regex pattern strings
MONTHS_MATCH_REGEX = iter_to_regex(MONTH_SHORTNAMES)
WEEKDAY_MATCH_REGEX = iter_to_regex(WEEKDAY_SHORTNAMES)
TIME_INTERVAL_REGEX = iter_to_regex(TIME_INTERVAL_TYPES.keys())
NUMBER_WORDS_REGEX = iter_to_regex(NUMBER_WORDS)

INTERVAL_PREPOSITION_REGEX = (
    iter_to_regex(POSITIVE_INTERVAL_WORDS)
    + "|"
    + iter_to_regex(NEGATIVE_INTERVAL_WORDS)
)


# compile patterns
# of the form "oct 20" "october 20" "10-20-2023
MDY_DATE_PATTERN = re.compile(
    whitespace_buffer
    + r"(?P<month>"
    + MONTHS_MATCH_REGEX
    + r"|\d+)[^\d\n]+?(?P<day>\d{1,2})(?P<year>[^\d\n]+\d{4})?"
    + whitespace_buffer
)

# phrases of the form "a week from"
RELATIVE_INTERVAL_PATTERN = re.compile(
    whitespace_buffer
    + r"(?P<time_unit_count>a\s*|"
    + NUMBER_WORDS_REGEX
    + r")?\s*(?P<time_interval_name>"
    + TIME_INTERVAL_REGEX
    + r")\w*[^\n\d\w]*(?P<preposition>"
    + INTERVAL_PREPOSITION_REGEX
    + ")"
    + whitespace_buffer
)

# phrases of the form "in ten days", "in two weeks"
IN_N_INTERVALS_PATTERN = re.compile(
    whitespace_buffer
    + r"in[^\n\d\w](?P<days_number>\w+|a)[^\n\d\w](?P<time_interval_name>"
    + TIME_INTERVAL_REGEX
    + r")\w*?"
    + whitespace_buffer
)

# phrases of the form "this sunday", "next wednesday"
RELATIVE_WEEKDAY_PATTERN = re.compile(
    whitespace_buffer
    + r"(?P<specifier>this|next)?[^\n\d\w]*(?P<weekday_name>"
    + WEEKDAY_MATCH_REGEX
    + ")"
    + whitespace_buffer
)
