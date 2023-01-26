from re import Pattern
from re import Match
from re import finditer

from typing import Iterable
from typing import Callable

from datetime import date
from datetime import timedelta

from itertools import chain

from functools import singledispatchmethod
from typing import Type
from typing import NamedTuple
from types import SimpleNamespace

from regex_utils import TIME_INTERVAL_TYPES
from regex_utils import NEGATIVE_INTERVAL_WORDS
from regex_utils import WEEKDAY_SHORTNAMES
from regex_utils import MONTH_SHORTNAMES

from regex_utils import MDY_DATE_PATTERN
from regex_utils import IN_N_INTERVALS_PATTERN
from regex_utils import RELATIVE_WEEKDAY_PATTERN
from regex_utils import RELATIVE_INTERVAL_PATTERN
from regex_utils import QUICK_DAYS_PATTERN


from regex_utils import NUMBER_WORDS


absolute_patterns = [
    MDY_DATE_PATTERN,
    IN_N_INTERVALS_PATTERN,
    RELATIVE_WEEKDAY_PATTERN,
    QUICK_DAYS_PATTERN,
]
relative_patterns = [RELATIVE_INTERVAL_PATTERN]


class DateTuple(NamedTuple):
    pattern: Pattern
    content: str
    start: int
    end: int


def quick_day_parse(date_match: Match, base_date: date) -> date:

    """Parse function for "today", "tomorrow", "yesterday" """

    offset = timedelta(
        days={"today": 0, "tomorrow": 1, "yesterday": -1}[date_match["quick_dayname"]]
    )

    return base_date + offset


class Changeme(SimpleNamespace):

    parse_funcs: dict[Pattern, Callable]

    def extract_regex_matches(self, text: str) -> list[Match]:

        return list(
            chain.from_iterable(
                (finditer(pattern, text) for pattern in self.parse_funcs)
            )
        )

    def match_to_tuple(self, match: Match) -> DateTuple:
        if not match.re in self.parse_funcs:
            raise ValueError("Match cannot be converted: not a known pattern")

        return DateTuple(
            pattern=match.re,
            content=match.group(),
            start=match.start(),
            end=match.end(),
        )

    @singledispatchmethod
    def ordered_matches(self, *args, **kwargs):
        raise NotImplementedError

    @ordered_matches.register
    def _(self, dates: list[DateTuple]) -> list[DateTuple]:
        """Sort DateTuple objects by order of occurance in the original string."""

        start_sort = sorted(dates, key=lambda d: d.start)
        return sorted(start_sort, key=lambda d: d.end)

    @ordered_matches.register
    def _(self, dates: list[Match]) -> list[Match]:
        """Sort regex match objects by order of occurance in the original string."""
        start_sort: list[Match] = sorted(dates, key=lambda m: m.start())
        return sorted(start_sort, key=lambda m: m.end())

    def group_expressions(self, dates: list[DateTuple]) -> list[list[DateTuple]]:  # type: ignore

        dates = self.ordered_matches(dates)
        
        

    def parse_subexpr(date_tuple, DateTuple) -> date | timedelta:  # type: ignore
        pass

    def reduce_expression(self, expr_elements: list[DateTuple]) -> date:  # type: ignore
        pass
