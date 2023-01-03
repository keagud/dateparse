from re import Pattern
from re import Match
from re import finditer


from typing import Iterable
from typing import Callable

from datetime import date
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class DateExpression:
    pattern: Pattern
    is_absolute: bool
    parse_func: Callable[[None], date]


@dataclass(frozen=True, kw_only=True)
class DateMatch:
    expression: DateExpression
    start_index: int
    end_index: int
    content: str
    match_obj: Match


class DateIter:
    def __init__(
        self, text: str, expressions: Iterable[DateExpression], reversed: bool = False
    ) -> None:
        self.text = text
        self.expressions = expressions
        self.reversed = reversed

    def __iter__(self):

        all_matches: list[DateMatch] = []

        match_iterators = (
            (expr, finditer(expr.pattern, self.text)) for expr in self.expressions
        )

        for match_expr, match_iter in match_iterators:

            matches = [
                DateMatch(
                    expression=match_expr,
                    content=match.group(),
                    start_index=match.start(),
                    end_index=match.end(),
                    match_obj=match,
                )
                for match in match_iter
                if match
            ]

            all_matches.extend(matches)

        all_matches.sort(key=lambda x: x.start_index, reverse=self.reversed)

        for match in all_matches:
            yield match
