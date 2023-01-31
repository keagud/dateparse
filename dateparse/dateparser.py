"""

    Defines a class for parsing multiple dates while maintaining 
    a persistant base date and user-defined named days.

    DateParser: Main interface class for stateful parsing

        __init__(base_date = None, named_days = None) -> None:


        sub_named_days(text: str)

        get_first(text: str)

        get_last(text: str)


        get_first_date(text: str)
        get_last_date(text: str)


"""
import datetime
from .parsefunctions import DateResult
from .parseutil import basic_parse
from .parseutil import iter_parse


class DateParser:

    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(
        self,
        base_date: datetime.date | None = None,
        named_days: dict[str, str] | None = None,
    ):

        self.named_days = self.default_named_days

        if named_days is not None:
            self.named_days.update(named_days)

        if base_date is None:
            base_date = datetime.date.today()
        self.base_date = base_date

    def sub_named_days(self, text: str):

        """
        Substitutes all substrings in the input for their corresponding value in self.named_days.
        Returns the processed string.
        """
        text = text.lower()

        for day_name, repl_str in self.named_days.items():
            if day_name in text:
                text = text.replace(day_name, repl_str)
        return text

    def get_first(self, text: str, allow_past: bool = False) -> DateResult | None:
        text = self.sub_named_days(text)
        return basic_parse(self.base_date, text, allow_past=allow_past)

    def get_first_date(
        self, text: str, allow_past: bool = False
    ) -> datetime.date | None:
        text = self.sub_named_days(text)
        result = basic_parse(self.base_date, text, allow_past=allow_past)

        if result is not None:
            return result.date
        return None

    def get_last(self, text: str, allow_past: bool = False):
        text = self.sub_named_days(text)
        return basic_parse(self.base_date, text, from_right=True, allow_past=allow_past)

    def get_last_date(self, text: str, allow_past: bool = False):
        text = self.sub_named_days(text)
        result = basic_parse(
            self.base_date, text, from_right=True, allow_past=allow_past
        )

        if result is not None:
            return result.date
        return None

    def iter_dates(self, text: str, from_right: bool = False, allow_past: bool = False):
        text = self.sub_named_days(text)
        return iter_parse(
            self.base_date, text, from_right=from_right, allow_past=allow_past
        )
