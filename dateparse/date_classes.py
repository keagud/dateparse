from re import Pattern
from re import Match
from re import finditer

from .regex_utils import TIME_INTERVAL_TYPES
from .regex_utils import NEGATIVE_INTERVAL_WORDS, POSITIVE_INTERVAL_WORDS
from .regex_utils import WEEKDAY_SHORTNAMES
from .regex_utils import MONTH_SHORTNAMES

from .regex_utils import MDY_DATE_PATTERN
from .regex_utils import IN_N_INTERVALS_PATTERN
from .regex_utils import RELATIVE_WEEKDAY_PATTERN
from .regex_utils import RELATIVE_INTERVAL_PATTERN


from typing import Iterable
from typing import Callable

from datetime import date
from datetime import timedelta

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class DateExpression:
    pattern: Pattern
    parse_func: Callable[..., date | timedelta]
    is_absolute: bool = True


class DateMatch:
    __slots__ = (
        "expression",
        "start_index",
        "end_index",
        "content",
        "base_match",
        "match_groups",
    )

    def __init__(self, expression: DateExpression, match_obj: Match) -> None:

        self.expression: DateExpression = expression
        self.start_index: int = match_obj.start()
        self.end_index: int = match_obj.end()
        self.content: str = match_obj.group()
        self.base_match: Match[str] = match_obj

        self.match_groups: dict = match_obj.groupdict()

    def to_date(self, *args, **kwargs):
        return self.expression.parse_func(self, *args, **kwargs)


class DateIter:
    def __init__(
        self,
        text: str,
        expressions: Iterable[DateExpression],
        reversed: bool = True,
        consecutive: bool = True,
    ) -> None:
        self.text = text
        self.expressions = expressions
        self.reversed = reversed
        self.consecutive = consecutive

    def _get_consecutive(self, matches_list: list[DateMatch]) -> list[DateMatch]:
        """
        Given a list of DateMatch objects, returns the initial segment of objects that are consecutive within the original string.
        """

        # TODO refactor to be less ugly
        prev: DateMatch | None = None
        consecutive_list = []

        for match in matches_list:
            if prev is not None:
                forward_diff = abs(match.start_index - prev.end_index)
                backward_diff = abs(match.end_index - prev.start_index)

                if forward_diff > 1 or backward_diff > 1:
                    break

            consecutive_list.append(match)
            prev = match

        return consecutive_list

    def __iter__(self):

        all_matches: list[DateMatch] = []

        match_iterators = (
            (expr, finditer(expr.pattern, self.text)) for expr in self.expressions
        )

        for match_expr, match_iter in match_iterators:

            matches = [
                DateMatch(
                    expression=match_expr,
                    match_obj=match,
                )
                for match in match_iter
                if match
            ]

            all_matches.extend(matches)

        all_matches.sort(key=lambda x: x.start_index, reverse=self.reversed)

        if self.consecutive:
            all_matches = self._get_consecutive(all_matches)

        for match in all_matches:

            yield match

    def __next__(self):
        pass




def match_to_dict(obj: DateMatch | dict[str, str]) -> dict[str, str]:
    if isinstance(obj, DateMatch):
        return obj.match_groups
    return obj


def mdy_parse(date_match: dict[str, str] | DateMatch, base_date: date) -> date:

    date_match = match_to_dict(date_match)

    month_str: str = date_match["month"]
    day_str: str = date_match["day"]

    if not month_str.isnumeric():
        month = MONTH_SHORTNAMES.index(month_str)
    else:
        month = int(month_str)

    day = int(day_str)

    year = int(date_match["year"]) if date_match["year"] else base_date.year

    return date(year, month, day)


def n_intervals_parse(date_match: DateMatch | dict[str, str], base_date: date) -> date:

    date_match = match_to_dict(date_match)

    days_num = int(date_match["days_number"])
    interval_name_str = date_match["time_interval_name"]

    days_offset = timedelta(days=TIME_INTERVAL_TYPES[interval_name_str] * days_num)

    return base_date + days_offset


def relative_weekday_parse(
    date_match: DateMatch | dict[str, str], base_date: date
) -> date:
    date_match = match_to_dict(date_match)

    specifier = date_match["specifier"]
    weekday_str = date_match["weekday_name"]

    weekday_num: int = WEEKDAY_SHORTNAMES.index(weekday_str)

    days_delta = weekday_num - base_date.isoweekday()

    # TODO refactor this to be less bad
    if days_delta <= 0:
        days_delta += 7

    if days_delta < 7 and specifier == "next":
        days_delta += 7

    return base_date + timedelta(days=days_delta)

def relative_interval_parse(
    date_match: dict[str, str] | DateMatch, base_date: date
) -> timedelta:

    date_match = match_to_dict(date_match)

    unit_count = int(date_match["time_unit_count"])
    interval_name_str = date_match["time_interval_name"]
    preposition = date_match["preposition"]
    days_offset = timedelta(days=unit_count * TIME_INTERVAL_TYPES[interval_name_str])

    if preposition in NEGATIVE_INTERVAL_WORDS:
        days_offset *= -1

    return days_offset



date_expressions = (
    DateExpression(pattern=MDY_DATE_PATTERN, parse_func=mdy_parse),
    DateExpression(
        pattern=RELATIVE_INTERVAL_PATTERN,
        parse_func=relative_interval_parse,
        is_absolute=False,
    ),
    DateExpression(pattern=IN_N_INTERVALS_PATTERN, parse_func=n_intervals_parse),
    DateExpression(pattern=RELATIVE_WEEKDAY_PATTERN, parse_func=relative_weekday_parse),
)
