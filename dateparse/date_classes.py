from re import Pattern
from re import Match
from re import finditer


from typing import Iterable
from typing import Callable
from typing import Any

from datetime import date
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class DateExpression:
    pattern: Pattern
    parse_func: Callable[..., date]
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

    def to_date(self):
        return self.expression.parse_func(self)


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
                    match_obj=match,
                )
                for match in match_iter
                if match
            ]

            all_matches.extend(matches)

        all_matches.sort(key=lambda x: x.start_index, reverse=self.reversed)

        for match in all_matches:
            yield match
