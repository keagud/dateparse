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


class DateMatch:
    # TODO depending on performance, may want to use __slots__
    # this would prevent the use of setattr and thus direct use of dot syntax for group labels
    # which would impact readability, but not much else
    def __init__(self, expression: DateExpression, match_obj: Match) -> None:

        self.expression = expression
        self.start_index, self.end_index = match_obj.span()
        self.content: str = match_obj.group()
        self.base_match = match_obj

        self.match_groups = match_obj.groupdict()

        for label, match_content in self.match_groups:
            setattr(self, label, match_content)


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
