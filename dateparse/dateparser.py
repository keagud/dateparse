"""
Defines the DateParser class, which wraps parse functionality
while remembering user-defined preferences
"""

import datetime

from .parsefunctions import DateResult
from .parseutil import basic_parse, parse_all, parse_all_dates


class DateParser:
    """
       Defines a class for parsing multiple dates while maintaining
       a persistant base date and user-defined named days.


       __init__(base_date = None, named_days = None) -> None:
           base_date: a datetime.date object to be used as the reference to
           any parse function calls from this class's methods.
           If unspecified or None, defaults to the current date (datetime.date.today())

           named_days: a dictionary with string keys and values. For example:
            {"my birthday":"september 9"}

            before parsing a string, all instances of each key will
            be replaced with the corresponding value

            A default pre-defined dictionary of named dates containing all (American) holidays with
            a fixed date representation is always enabled in addition.

       sub_named_days(text: str)
           Substitutes each occurrence of a key in self.named_days for its value.
           Returns the modified string

       get_first(text: str) -> DateResult | None
       get_last(text: str) -> DateResult | None

           Get the first or last occurrence of date expression within the text.
           Both return a DateResult object.
           A DateResult is a named tuple (typing.NamedTuple) defined in parsefunctions.py


       get_first_date(text: str) -> datetime.date | None
       get_last_date(text: str) -> datetime.date | None

           Identical to get_first and get_last, respectively,
           but will return only the date for convenience.

    get_all(
        text: str,
        from_right: bool = False,
        allow_past: bool = False
            ) -> list[datetime.date] | None

    get_all_dates(
        text: str,
        from_right: bool = False,
        allow_past: bool = False
            ) -> list[datetime.date] | None:

       These both get all dates found in the input text, and return them as a list.
       get_all returns a list of DateResult tuples,
       and get_all_dates returns a list of bare datetime.date objects; this is the only difference

    """

    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(
        self,
        base_date: datetime.date | None = None,
        named_days: dict[str, str] | None = None,
    ):

        """
        Constructor for DateParser

        """

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
        """Returns a DateResult tuple for the leftmost date expression in the input"""
        text = self.sub_named_days(text)
        return basic_parse(self.base_date, text, allow_past=allow_past)

    def get_first_date(
        self, text: str, allow_past: bool = False
    ) -> datetime.date | None:
        """Returns a datetime.date for the leftmost date expression in the input"""
        text = self.sub_named_days(text)
        result = basic_parse(self.base_date, text, allow_past=allow_past)

        if result is not None:
            return result.date
        return None

    def get_last(self, text: str, allow_past: bool = False):
        """Returns a DateResult tuple for the rightmost date expression in the input"""
        text = self.sub_named_days(text)
        return basic_parse(self.base_date, text, from_right=True, allow_past=allow_past)

    def get_last_date(self, text: str, allow_past: bool = False):
        """Returns a datetime.date for the rightmost date expression in the input"""
        text = self.sub_named_days(text)
        result = basic_parse(
            self.base_date, text, from_right=True, allow_past=allow_past
        )

        if result is not None:
            return result.date
        return None

    def get_all(
        self, text: str, from_right: bool = False, allow_past: bool = False
    ) -> list[DateResult] | None:
        """Returns a list of all found date expressions as DateResult tuples"""
        text = self.sub_named_days(text)
        return parse_all(
            self.base_date, text, from_right=from_right, allow_past=allow_past
        )

    def get_all_dates(
        self, text: str, from_right: bool = False, allow_past: bool = False
    ) -> list[datetime.date] | None:
        """Returns a list of all found date expressions as datetime.date objects"""
        text = self.sub_named_days(text)
        return parse_all_dates(
            self.base_date, text, from_right=from_right, allow_past=allow_past
        )
