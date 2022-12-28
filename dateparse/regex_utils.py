import re
from collections import namedtuple
from typing import Any
from itertools import chain


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


TIME_INTERVAL_TYPES = ["day", "week", "month", "year"]

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
def list_to_regex(input_list: list) -> str:
    return "|".join([s for s in input_list if s])


# make regex pattern strings
MONTHS_MATCH_REGEX = list_to_regex(MONTH_SHORTNAMES)
WEEKDAY_MATCH_REGEX = list_to_regex(WEEKDAY_SHORTNAMES)
TIME_INTERVAL_REGEX = list_to_regex(TIME_INTERVAL_TYPES)
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
    r"(" + MONTHS_MATCH_REGEX + r"|\d+)[^\d\n]+?(\d{1,2})([^\d\n]+\d{4})?"
)

# phrases of the form "a week from"
RELATIVE_INTERVAL_PATTERN = re.compile(
    r"(a\s*|"
    + NUMBER_WORDS_REGEX
    + r")?\s*("
    + TIME_INTERVAL_REGEX
    + r")\w*[^\n\d\w]*("
    + INTERVAL_PREPOSITION_REGEX
    + ")"
)

# phrases of the form "in ten days", "in two weeks"
IN_N_INTERVALS_PATTERN = re.compile(
    r"in[^\n\d\w](\w+|a)[^\n\d\w](" + TIME_INTERVAL_REGEX + r")\w*?"
)

# phrases of the form "this sunday", "next wednesday"
RELATIVE_WEEKDAY_PATTERN = re.compile(
    r"(this|next)?[^\n\d\w]*(" + WEEKDAY_MATCH_REGEX + ")"
)


_patterns_dict = {
    "month_day": MDY_DATE_PATTERN,
    "in_n_intervals": IN_N_INTERVALS_PATTERN,
    "relative_weekday": RELATIVE_WEEKDAY_PATTERN,
    "relative_interval": RELATIVE_INTERVAL_PATTERN,
}

_WrapPatterns = namedtuple("_WrapPatterns", ",".join(_patterns_dict))

date_patterns = _WrapPatterns(**_patterns_dict)


# UTILITY FUNCTIONS FOR REGEX


def iter_all_matches(
    text: str, patterns: list[re.Pattern[str]] | list[str], reverse: bool = False
):

    """
    Yield all matches for any of the given patterns in the text, iterating left to right,
    or right to left if reversed is specified.
    """

    comp_patterns: list[re.Pattern] = [
        re.compile(p) if not isinstance(p, re.Pattern) else p for p in patterns
    ]

    match_iterators = [re.finditer(pattern, text) for pattern in comp_patterns]
    matches_list = list(chain.from_iterable(match_iterators))

    matches_list.sort(key=lambda x: x.start(), reverse=reverse)

    for match in matches_list:
        if match:
            yield match
