from re import Match

from regex_utils import MDY_DATE_PATTERN
from regex_utils import IN_N_INTERVALS_PATTERN
from regex_utils import RELATIVE_WEEKDAY_PATTERN
from regex_utils import RELATIVE_INTERVAL_PATTERN

from regex_utils import NUMBER_WORDS
from regex_utils import MONTH_SHORTNAMES

from date_classes import DateExpression, DateMatch


def mdy_parse(date_match: Match | DateMatch):

    if isinstance(date_match, DateMatch):
        date_match = date_match.match_obj

    month, day = date_match.groupdict


    








