import datetime
from .parseutil import basic_parse


class DateParser:

    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(self):
        self.named_days = self.default_named_days

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

    def get_first(self, base_date: datetime.date, text: str):
        pass

    def get_first_date(self, base_date: datetime.date, text: str):
        pass
