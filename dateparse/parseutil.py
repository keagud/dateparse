import typing
import math

from typing import Iterable
import datetime
import re
import functools as fn
import itertools as it


class DateTuple(typing.NamedTuple):
    """Container for data about a matched date expression"""

    pattern: re.Pattern
    fields: dict
    content: str
    start: int
    end: int


def _extract_regex_matches(
    text: str, pattern_set: Iterable[re.Pattern]
) -> list[re.Match]:

    match_chain = it.chain.from_iterable(

        (re.finditer(pattern, text) for pattern in pattern_set)
    )

    return list(match_chain)


def _match_to_tuple(match: re.Match):

    return DateTuple(
        pattern=match.re,
        content=match.group(),
        fields=match.groupdict(),
        start=match.start(),
        end=match.end(),
    )


def _remove_subgroups(dates: list[DateTuple]):

    # remove any matches fully contained within another match
    for first, second, third in zip(dates[:-1], dates[1:-1], dates[2:]):
        if (second.start >= first.start and second.end <= first.end) or (
            second.start >= third.start and second.end <= third.end
        ):
            dates.remove(second)

    return dates


def _ordered_matches(dates: list[DateTuple]) -> list[DateTuple]:
    start_sort = sorted(dates, key=lambda d: d.start)
    return sorted(start_sort, key=lambda d: d.end)


def _reduce_exprs(
    absolute_patterns: Iterable[re.Pattern],
    exprs_list: list[list[DateTuple]],
    dates_set: list[DateTuple],
):
    groups = _make_groups(dates_set, absolute_patterns)
    exprs_list.extend(groups)

    return exprs_list


def preprocess_input(
    text: str,
    absolute_patterns: Iterable[re.Pattern],
    relative_patterns: Iterable[re.Pattern],
):

    import ipdb; ipdb.set_trace()
    # find all regex matches, convert to DateTuple objects, and sort by occurrence in the string
    pattern_set = list(it.chain(absolute_patterns, relative_patterns))
    regex_matches = _extract_regex_matches(text, pattern_set)

    match_tuples = [_match_to_tuple(m) for m in regex_matches]

    match_tuples = _ordered_matches(match_tuples)

    # group date tuples
    all_groups: list[list[DateTuple]] = []
    this_group: list[DateTuple] = []

    for tup in match_tuples:

        if tup.pattern in absolute_patterns:
            this_group.append(tup)
            all_groups.append(this_group)
            this_group = []
            continue

        if this_group and not math.isclose(this_group[-1].end, tup.start, rel_tol=1):
            this_group = []
            continue

        this_group.append(tup)

    return all_groups


def _group_expressions(
    dates: list[DateTuple],
    absolute_patterns: Iterable[re.Pattern],
    relative_patterns: Iterable[re.Pattern],
) -> list[list[DateTuple]]:
    """
    Group expressions into sublists, representing a string of consecutive expressions of
    this form: any number of relative expressions followed by exactly one absolute expression.
    # enforce each group to consist of any number of relative expressions
    # + exactly one absolute expression
    """

    reduce_fn = fn.partial(_reduce_exprs, absolute_patterns)
    consec_groups = _make_groups(dates, absolute_patterns)

    groups = fn.reduce(reduce_fn, consec_groups, [])
    return groups
