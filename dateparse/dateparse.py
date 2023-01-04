from functools import reduce
from datetime import date, timedelta
from typing import Iterator
from operator import add

from ._parse_util import DateMatch
from ._parse_util import DateMatch
from ._parse_util import DateIter
from ._parse_util import date_expressions as defined_date_exprs


class DateParser:
    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(
        self, current_date: date | None = None, named_days: dict[str, str] | None = None
    ) -> None:

        self.date_expressions = defined_date_exprs

        self.current_date = current_date if current_date is not None else date.today()

        self.named_days = self.default_named_days

        if named_days is not None:
            self.named_days.update(named_days)

    def sub_named_days(self, text: str):

        text = text.lower()

        for day_name, repl_str in self.named_days.items():
            if day_name in text:
                text = text.replace(day_name, repl_str)
        return text

    def iter_match_tokens(self, text: str) -> Iterator[DateMatch]:
        text = self.sub_named_days(text)
        date_iter = DateIter(text, self.date_expressions)
        return ((match) for match in date_iter)

    def parse_date_match(self, date_match: DateMatch) -> date | timedelta:
        return date_match.to_date(self.current_date)

    def parse_tokens(
        self, match_iter: Iterator[DateMatch]
    ) -> Iterator[date | timedelta]:
        return ((match.to_date(self.current_date)) for match in match_iter)

    def parse_date(self, text: str) -> date:
        """
        Main wrapper method for converting a complex string expression to a datetime.date object.
        Input: text as a string
        Output: datetime.date object
        If no known date format patterns are matched, raises a ValueError
        """

        text_lower = self.sub_named_days(text)
        dates_iter = self.parse_tokens(self.iter_match_tokens(text_lower))

        deltas: list[timedelta] = []

        abs_date: date | None = None

        for date_item in dates_iter:
            if not isinstance(date_item, timedelta):
                abs_date = date_item
                break

            deltas.append(date_item)

        if abs_date is None:
            raise ValueError(f"Could not find a date anchor in input text '{text}'")

        offset: timedelta = reduce(add, deltas) if deltas else timedelta(days=0)

        return abs_date + offset
