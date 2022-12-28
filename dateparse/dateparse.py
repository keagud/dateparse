import re
from re import Match
from datetime import date, timedelta


from regex_utils import date_patterns, iter_all_matches


class DateParser:
    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(
        self, current_date: date | None = None, named_days: dict[str, str] | None = None
    ) -> None:

        self.current_date = current_date if current_date is not None else date.today()

        self.named_days = self.default_named_days

        if named_days is not None:
            self.named_days.update(named_days)

        for pattern_name, pattern_content in date_patterns._asdict().values():
            setattr(self, "_" + pattern_name, pattern_content)

    def match_date_expressions(self, expression_str: str) -> list[Match]:  # type: ignore
        """Returns a list of re.Match objects, matching tokens in the input string that can be resolved into either a date or timedelta object."""
        pass

    def parse_date_token(token: str) -> date:  # type: ignore
        """Converts a single date token (e.g. 'October 11', 'Christmas', 'tomorrow') into a datetime.date object."""

        pass

    def parse_timedelta_token(token: str) -> timedelta:  # type: ignore
        """Converts a string representing a time interval (e.g. 'a week from', 'the day after') into a datetime.timedelta object."""
        pass

    def evaluate_date_tokens(date_token: date, deltas=list[timedelta] | None) -> date:  # type: ignore
        """Takes a datetime.date object and an optional list of datetime.timedelta objects. Sums the date with the timedeltas."""
        pass
