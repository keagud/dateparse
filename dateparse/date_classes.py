import re
from re import Match
from re import Pattern

from datetime import date
from dataclasses import dataclass
from itertools import chain


class DateExpression:
    def __init__(self, pattern: Pattern, is_absolute: bool = False) -> None:
        self.pattern = pattern
        self.is_absolute = is_absolute


@dataclass(frozen=True, kw_only=True)
class DateMatch:
    expression: DateExpression
    start_index: int
    end_index: int
    content: str


class DateIter:
    def __init__(self, input_text: str, expressions: list[DateExpression]) -> None:

        self.input_text = input_text
        self.expressions = expressions

    def _list_all_matches(
        self,
        text: str,
        patterns: list[re.Pattern[str]] | list[str],
        reverse: bool = False,
    ) -> list[Match[str]]:

        """
        Returns a list of all matches for any of the given patterns in the text,
        iterating left to right, or right to left if reversed is specified.
        """

        comp_patterns: list[re.Pattern] = [
            re.compile(p) if not isinstance(p, re.Pattern) else p for p in patterns
        ]

        match_iterators = [re.finditer(pattern, text) for pattern in comp_patterns]
        matches_list = list(chain.from_iterable(match_iterators))

        matches_list.sort(key=lambda x: x.start(), reverse=reverse)

        return matches_list

    def _regex_to_datematch(self, expr: DateExpression, m: Match):
        content: str = m.group()

        if not content:
            return None

        start_index, end_index = m.span()

        return DateMatch(
            expression=expr,
            start_index=start_index,
            end_index=end_index,
            content=content,
        )

    def __iter__(self):

        match_iterators = (
            ((expr, re.finditer(expr.pattern, self.input_text)))
            for expr in self.expressions
        )

        # yield a DateMatch

        all_matches = []

        for match_iter_content in match_iterators:

            matched_expr, expr_iter = match_iter_content

            matches_from_date_expr = [
                i
                for i in map(
                    lambda x: self._regex_to_datematch(matched_expr, x), expr_iter
                )
                if i is not None
            ]

            all_matches.append(matches_from_date_expr)

        all_matches.sort(key=lambda x: x.start_index)

        for datematch in all_matches:
            yield datematch
