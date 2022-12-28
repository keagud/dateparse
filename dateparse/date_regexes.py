import re

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

named_days = {
    "christmas": "dec 25",
    "new years": "jan 1",
    "halloween": "oct 31",
}  # TODO allow user to add to this
# also TODO let this be used in the parser- currently it does not

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
DATE_PATTERN = re.compile(
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


# collects the patterns refering to absolute dates
# e.g. dates that are associated unambiguously with a datetime.date expression
# these expressions are used by the parser to "anchor" any other time expressions to a date


ABSOLUTE_DATE_PATTERNS = (
    DATE_PATTERN,
    IN_N_INTERVALS_PATTERN,
    RELATIVE_WEEKDAY_PATTERN,
)
