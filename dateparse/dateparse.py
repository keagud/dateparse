import re
from re import Match
from datetime import date, timedelta
from itertools import chain

from regex_utils import DatePatterns, list_to_regex


class DateParser:
    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(
        self, current_date: date | None = None, named_days: dict[str, str] | None = None
    ) -> None:

        self.current_date = current_date if current_date is not None else date.today()

        self.named_days = self.default_named_days

        if named_days is not None:
            self.named_days.update(named_days)

        _named_day_titles = list(self.named_days.keys())
        _named_days_regex = re.compile(list_to_regex(_named_day_titles))

        self.date_patterns = DatePatterns(named_days=_named_days_regex)

        for x in self.date_patterns:
            pass

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

    def _get_match_name(self, match: Match) -> str | None:
        for name, pattern in vars(self.date_patterns).items():
            if pattern == match.re:
                return name

    def tokenize_date_string(self, text: str) -> list[Match]:
        """Break an input string into a list of tokens matching a date pattern"""
        return self._list_all_matches(text, list(self.date_patterns))

    def parse_date_token(self, token: str | Match[str]) -> date:  # type: ignore
        """Converts a single date token (e.g. 'October 11', 'Christmas', 'tomorrow') into a datetime.date object."""

        #  if token.lower() in ((d.lower()) for d in self.named_days):

        pass

    def parse_timedelta_token(token: str) -> timedelta:  # type: ignore
        """Converts a string representing a time interval (e.g. 'a week from', 'the day after') into a datetime.timedelta object."""
        pass

    def evaluate_date_tokens(date_token: date, deltas=list[timedelta] | None) -> date:  # type: ignore
        """Takes a datetime.date object and an optional list of datetime.timedelta objects. Sums the date with the timedeltas."""
        pass
