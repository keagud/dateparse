import re
from re import Pattern
from collections import namedtuple
from dataclasses import dataclass

from datetime import date


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
]  # one-indexed for symmetry with MONTH_SHORTNAMES[] mostly


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

# utility function to convert a list of strings to a
# regex pattern string matching any element in the list
# returned as a string rather than re.Pattern to allow further recombination
def list_to_regex(input_list: list[str]) -> str:
    return "|".join([s for s in input_list if s])


# make regex pattern strings
MONTHS_MATCH_REGEX = list_to_regex(MONTH_SHORTNAMES)
WEEKDAY_MATCH_REGEX = list_to_regex(WEEKDAY_SHORTNAMES)
TIME_INTERVAL_REGEX = list_to_regex(list(TIME_INTERVAL_TYPES.keys()))
NUMBER_WORDS_REGEX = list_to_regex(NUMBER_WORDS)

INTERVAL_PREPOSITION_REGEX = (
    list_to_regex(POSITIVE_INTERVAL_WORDS)
    + "|"
    + list_to_regex(NEGATIVE_INTERVAL_WORDS)
)

# if additional named days beyond the defaults were specified, include those

# compile patterns

# of the form "oct 20" "october 20" "10-20-2023
MDY_DATE_PATTERN = re.compile(
    r"(?P<month>"
    + MONTHS_MATCH_REGEX
    + r"|\d+)[^\d\n]+?(?P<day>\d{1,2})(?P<year>[^\d\n]+\d{4})?"
)

# phrases of the form "a week from"
RELATIVE_INTERVAL_PATTERN = re.compile(
    r"(?P<time_unit_count>a\s*|"
    + NUMBER_WORDS_REGEX
    + r")?\s*(?P<time_interval_name>"
    + TIME_INTERVAL_REGEX
    + r")\w*[^\n\d\w]*(?P<preposition>"
    + INTERVAL_PREPOSITION_REGEX
    + ")"
)

# phrases of the form "in ten days", "in two weeks"
IN_N_INTERVALS_PATTERN = re.compile(
    r"in[^\n\d\w](?P<days_number>\w+|a)[^\n\d\w](?P<time_interval_name>"
    + TIME_INTERVAL_REGEX
    + r")\w*?"
)

# phrases of the form "this sunday", "next wednesday"
RELATIVE_WEEKDAY_PATTERN = re.compile(
    r"(?P<specifier>this|next)?[^\n\d\w]*(?P<weekday_name>" + WEEKDAY_MATCH_REGEX + ")"
)


@dataclass(frozen=True, kw_only=True)
class DatePatterns:

    month_day: Pattern = MDY_DATE_PATTERN
    in_n_intervals: Pattern = IN_N_INTERVALS_PATTERN
    relative_weekday: Pattern = RELATIVE_WEEKDAY_PATTERN
    relative_interval: Pattern = RELATIVE_INTERVAL_PATTERN
    named_days: Pattern

    def get_absolute_patterns(self) -> list[Pattern]:
        return [self.month_day, self.in_n_intervals, self.relative_weekday]

    def __iter__(self):
        for p in self.get_absolute_patterns():
            yield p

        yield self.relative_interval
        yield self.named_days


@dataclass(frozen=True)
class DatePattern:
    pattern: re.Pattern
    is_absolute: bool

    pass


@dataclass(frozen=True, kw_only=True)
class DateMatch:
    content: str
    start_index: int
    end_index: int
    is_absolute: bool


class DateIter:
    def __init__(self, input_text: str, named_days: dict = {}) -> None:
        pass
