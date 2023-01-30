from re import Pattern
from re import Match
from re import finditer

from typing import Iterator
from typing import Callable
from typing import NamedTuple

from datetime import date
from datetime import timedelta
from functools import reduce


from itertools import chain

from .parsefunctions import absolute_patterns
from .parsefunctions import DateTuple

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


