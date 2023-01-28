from re import Pattern
from re import Match
from re import finditer

from typing import Iterator
from typing import Callable

from datetime import date, time
from datetime import timedelta

from itertools import chain

from functools import reduce, singledispatchmethod

from types import SimpleNamespace

from .parse_functions import absolute_patterns
from .parse_functions import relative_patterns

from .parse_functions import DateTuple
from .parse_functions import absolute_functions_index
from .parse_functions import relative_functions_index


class DateProcessor(SimpleNamespace):

    parse_funcs: dict[Pattern, Callable] = (
        absolute_functions_index | relative_functions_index
    )

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
            fields=match.groupdict(),
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

    def group_expressions(self, dates: list[DateTuple]) -> list[list[DateTuple]]:
        """
        Group expressions into sublists, representing a string of consecutive expressions of
        this form: any number of relative expressions followed by exactly one absolute expression.
        """

        def remove_subgroups(dates: list[DateTuple]):

            # remove any matches fully contained within another match
            for first, second, third in zip(dates[:-1], dates[1:-1], dates[2:]):
                if (second.start >= first.start and second.end <= first.end) or (
                    second.start >= third.start and second.end <= third.end
                ):
                    dates.remove(second)

            return dates

        # group consecutive matches
        def group_consecutive(dates: list[DateTuple]):
            consec_run = []
            for i in dates:
                if consec_run and consec_run[-1][1] != i[0]:
                    yield consec_run
                    consec_run = [i]
                    continue

                consec_run.append(i)
            yield consec_run

        # enforce each group to consist of any number of relative expressions
        # + exactly one absolute expression
        def make_groups(dates: list[DateTuple]):
            groups: list[list[DateTuple]] = []
            group: list[DateTuple] = []
            for d in dates:
                if d.pattern in absolute_patterns:
                    group.append(d)
                    groups.append(group)
                    group = []
                    continue

                group.append(d)
            return groups

        dates = remove_subgroups(self.ordered_matches(dates))

        return reduce(
            lambda a, b: a + make_groups(b), group_consecutive(dates), initial=[]
        )

    def parse_subexpr(self, date_tuple: DateTuple) -> date | timedelta:
        """Converts a date tuple to a date or timedelta, by calling its corresponding function"""
        return self.parse_funcs[date_tuple.pattern](date_tuple.content)

    def reduce_expression_set(self, expr_elements: list[DateTuple]) -> date:
        """
        Takes a list of date tuples- any number that correspond to a relative date
        pattern, and exactly one corresponding to an absolute date pattern.
        Returns the date object created by summing them.
        """

        if not isinstance(anchor_date := self.parse_subexpr(expr_elements[-1]), date):
            raise ValueError

        if len(expr_elements) == 1:
            return anchor_date

        deltas: list[timedelta] = [
            parse_result
            for e in expr_elements[:-1]
            if isinstance(parse_result := self.parse_subexpr(e), timedelta)
        ]

        return anchor_date + reduce(lambda a, b: a + b, deltas)

    def iter_dates(self, text: str, from_right: bool = False) -> Iterator[date]:
        """Driver function to extract dates from text and iterate through them"""

        extracted_dates = [
            self.match_to_tuple(m) for m in self.extract_regex_matches(text)
        ]

        if from_right:
            extracted_dates.reverse()

        for expr_set in self.group_expressions(extracted_dates):
            yield self.reduce_expression_set(expr_set)