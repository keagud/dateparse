import math

from typing import Iterable
from typing import Callable
import datetime
import re
import functools as fn
import itertools as it

from .parsefunctions import absolute_functions_index
from .parsefunctions import relative_functions_index

from .parsefunctions import absolute_patterns
from .parsefunctions import relative_patterns

from .parsefunctions import DateTuple
from .parsefunctions import DateResult
from .parsefunctions import ExpressionGrouping


def sub_named_days(named_days: dict[str, str], text: str):

    """
    Substitutes all substrings in the input for their corresponding value in named_days.
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
    for first, second, third in zip(dates[:-1], dates[1:-1], dates[2:]):
        if (second.start >= first.start and second.end <= first.end) or (
            second.start >= third.start and second.end <= third.end
        ):
            dates.remove(second)

    return dates


def _ordered_matches(dates: list[DateTuple]) -> list[DateTuple]:
    start_sort = sorted(dates, key=lambda d: d.start)
    return sorted(start_sort, key=lambda d: d.end)


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
    match_tuples = [_match_to_tuple(m) for m in regex_matches]
    match_tuples = _ordered_matches(match_tuples)

    match_tuples = _remove_subgroups(match_tuples)

    # group date tuples
    all_groups: list[ExpressionGrouping] = []
    group_deltas: list[DateTuple] = []

    for tup in match_tuples:

        if tup.pattern in absolute_patterns:
            new_expr = ExpressionGrouping(anchor=tup, deltas=group_deltas)
            all_groups.append(new_expr)
            group_deltas = []
            continue

        if group_deltas and not math.isclose(
            group_deltas[-1].end, tup.start, rel_tol=1
        ):
            group_deltas = []
            continue

        group_deltas.append(tup)

    return all_groups


preprocess_input: Callable[[str], list[ExpressionGrouping]] = fn.partial(
    _partial_preprocess_input,
    absolute_patterns=absolute_patterns,
    relative_patterns=relative_patterns,
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
    [datetime.date, ExpressionGrouping], datetime.date
] = fn.partial(
    _partial_parse_expression_group,
    abs_index=absolute_functions_index,
    rel_index=relative_functions_index,
)


def get_expression_span(expr: ExpressionGrouping):

    if not expr.deltas:
        return (expr.anchor.start, expr.anchor.end)

    expr_start = min(d.start for d in expr.deltas)

    return (expr_start, expr.anchor.end)


def reduce_expression(base_date: datetime.date, expr: ExpressionGrouping):

    deltas = expr.deltas
    anchor = expr.anchor

    resulting_date = parse_expression_group(base_date, expr)
    start, end = get_expression_span(expr)

    delta_content = " ".join([d.content for d in deltas])

    expr_content = f"{delta_content} {anchor.content}".strip()

    new_date_result = DateResult(resulting_date, start, end, expr_content)

    return new_date_result


def basic_parse(base_date: datetime.date, text: str, from_right: bool = False):
    expressions = preprocess_input(text)

    if not expressions:
        return None

    target_expr = expressions[-1] if from_right else expressions[0]

    return reduce_expression(base_date, target_expr)


def iter_parse(base_date: datetime.date, text: str, from_right: bool = False):
    expressions = preprocess_input(text)

    if not expressions:
        return None

    if from_right:
        expressions.reverse()

    for expr in expressions:
        yield reduce_expression(base_date, expr)
