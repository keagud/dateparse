"""Defines public date parsing functions."""
import datetime
import functools as fn
import itertools as it
import re
from typing import Callable, Iterable

from .parsefunctions import (
    DateResult,
    DateTuple,
    ExpressionGrouping,
    absolute_functions_index,
    relative_functions_index,
)


def sub_named_days(named_days: dict[str, str], text: str):
    """
    Pre-process a string for named days (e.g. holidays)
    Parameters:
        named_days: dict[str,str]
        text: str

    Substitutes all substrings in text that match
    a key in named_days for their corresponding value.
    Returns the processed string.
    """
    text = text.lower()

    for day_name, repl_str in named_days.items():
        if day_name in text:
            text = text.replace(day_name, repl_str)
    return text


def _extract_regex_matches(
    text: str, pattern_set: Iterable[re.Pattern]
) -> list[re.Match]:

    match_chain = it.chain.from_iterable(
        (re.finditer(pattern, text) for pattern in pattern_set)
    )

    return list(match_chain)


def _match_to_tuple(match: re.Match) -> DateTuple:

    return DateTuple(
        pattern=match.re,
        content=match.group(),
        fields=match.groupdict(),
        start=match.start(),
        end=match.end(),
    )


def _remove_subgroups(dates: list[DateTuple]) -> list[DateTuple]:

    # remove any matches fully contained within another match
    iter_by_three = zip(dates[:-1], dates[1:-1], dates[2:])
    for first, second, third in iter_by_three:

        within_prior = second.start >= first.start and second.end <= first.end
        within_next = second.start >= third.start and second.end <= third.end

        if within_prior or within_next:
            dates.remove(second)

    return dates


def _ordered_matches(dates: list[DateTuple]) -> list[DateTuple]:
    start_sort = sorted(dates, key=lambda d: d.start)
    return sorted(start_sort, key=lambda d: d.end)


def _make_expression_groups(
    match_tuples: list[DateTuple], absolute_patterns: set[re.Pattern]
) -> list[ExpressionGrouping]:

    all_groups: list[ExpressionGrouping] = []
    group_deltas: list[DateTuple] = []

    for tup in match_tuples:
        if tup.pattern in absolute_patterns:
            new_expr = ExpressionGrouping(anchor=tup, deltas=group_deltas)
            all_groups.append(new_expr)
            group_deltas = []
            continue

        if not group_deltas:
            is_adjacent = False
        else:
            is_adjacent = (tup.start - group_deltas[-1].end) <= 1

        if is_adjacent:
            group_deltas = []
            continue

        group_deltas.append(tup)

    return all_groups


def _partial_preprocess_input(
    text: str,
    absolute_patterns: Iterable[re.Pattern] | None = None,
    relative_patterns: Iterable[re.Pattern] | None = None,
) -> list[ExpressionGrouping]:

    if absolute_patterns is None or relative_patterns is None:
        raise ValueError

    # find all regex matches, convert to DateTuple objects, and sort by occurrence in the string
    pattern_set = list(it.chain(absolute_patterns, relative_patterns))
    regex_matches = _extract_regex_matches(text, pattern_set)
    match_tuples = [_match_to_tuple(match) for match in regex_matches]
    match_tuples = _ordered_matches(match_tuples)

    match_tuples = _remove_subgroups(match_tuples)

    return _make_expression_groups(match_tuples, set(absolute_patterns))


preprocess_input: Callable[[str], list[ExpressionGrouping]] = fn.partial(
    _partial_preprocess_input,
    absolute_patterns=absolute_functions_index.keys(),
    relative_patterns=relative_functions_index.keys(),
)


def _partial_parse_expression_group(
    base_date: datetime.date,
    expr_group: ExpressionGrouping,
    abs_index=None,
    rel_index=None,
) -> datetime.date:

    if abs_index is None or rel_index is None:
        raise ValueError

    anchor_date_tuple = expr_group.anchor

    anchor_parser = abs_index[anchor_date_tuple.pattern]

    anchor_date = anchor_parser(anchor_date_tuple, base_date)

    delta_sum = datetime.timedelta(days=0)
    for delta in expr_group.deltas:
        delta_parser = rel_index[delta.pattern]
        delta_sum += delta_parser(delta, base_date)

    return anchor_date + delta_sum


parse_expression_group: Callable[
    [datetime.date, ExpressionGrouping],
    datetime.date,
] = fn.partial(
    _partial_parse_expression_group,
    abs_index=absolute_functions_index,
    rel_index=relative_functions_index,
)


def _get_expression_span(expr: ExpressionGrouping):

    if not expr.deltas:
        return (expr.anchor.start, expr.anchor.end)

    expr_start = min(delta_tup.start for delta_tup in expr.deltas)

    return (expr_start, expr.anchor.end)


def _reduce_expression(
    base_date: datetime.date, expr: ExpressionGrouping, allow_past: bool = False
):

    deltas = expr.deltas
    anchor = expr.anchor

    resulting_date = parse_expression_group(base_date, expr)

    if resulting_date.toordinal() < base_date.toordinal() and not allow_past:
        bumped_year = resulting_date.year + 1
        resulting_date = resulting_date.replace(year=bumped_year)

    start, end = _get_expression_span(expr)

    delta_content = " ".join([delta_tup.content.strip() for delta_tup in deltas])
    anchor_content = anchor.content.strip()

    expr_content = delta_content + " " + anchor_content

    new_date_result = DateResult(resulting_date, start, end, expr_content)

    return new_date_result


def basic_parse(
    base_date: datetime.date,
    text: str,
    from_right: bool = False,
    allow_past: bool = False,
):
    """
    Get a single date expression from a string, and return it as a DateResult tuple.

    Parameters:

        base_date: datetime.date
            The reference point date for interpreting a date expression with implicit reference
            to the present time.
            For example: "Next Thursday" is ambiguous without context.
            With a base_date of 2022-11-25, it can be unambiguously resolved to 2022-12-01.

        text: str
             The input text to be processed. It is scanned left to right by default, and the first
             substring to match a known date expression pattern is parsed and returned as a date.

        from_right: bool
            If true, begin scanning the text right to left (default: false)

        allow_past: bool
            If true, correct dates that precede the base date to their next occurrence after
            (default: false)

    Returns a DateResult tuple, a typed NamedTuple with fields for the date value, start and
    end indices, and matched substring. If no valid expression  was found, returns None

    """
    expressions = preprocess_input(text)

    if not expressions:
        return None

    target_expr = expressions[-1] if from_right else expressions[0]

    return _reduce_expression(base_date, target_expr, allow_past=allow_past)


def basic_date_parse(
    base_date: datetime.date,
    text: str,
    from_right: bool = False,
    allow_past: bool = False,
):

    """Same as basic_parse, but returns the date directly."""
    parsed_tuple = basic_parse(
        base_date, text, from_right=from_right, allow_past=allow_past
    )

    if parsed_tuple is None:
        return None

    return parsed_tuple.date


def parse_all(
    base_date: datetime.date,
    text: str,
    from_right: bool = False,
    allow_past: bool = False,
):
    """Get _all_ matched expressions as a list of DateResult tuples."""

    expressions = preprocess_input(text)

    if not expressions:
        return None

    if from_right:
        expressions.reverse()

    date_tuple_results = [
        _reduce_expression(base_date, expr, allow_past=allow_past)
        for expr in expressions
    ]

    return date_tuple_results


def parse_all_dates(
    base_date: datetime.date,
    text: str,
    from_right: bool = False,
    allow_past: bool = False,
):
    """Variant of parse_all that returns a list of datetime.date objects instead of DateResults."""

    parsed_tuples = parse_all(
        base_date,
        text,
        from_right=from_right,
        allow_past=allow_past,
    )

    if parsed_tuples is None:
        return None

    return [tup.date for tup in parsed_tuples]
