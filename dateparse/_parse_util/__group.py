from re import Pattern
from re import Match
from re import finditer

from typing import Iterable
from typing import Callable

from datetime import date
from datetime import timedelta

from dataclasses import dataclass
from functools import wraps
from functools import update_wrapper
from typing import Type

from regex_utils import TIME_INTERVAL_TYPES
from regex_utils import NEGATIVE_INTERVAL_WORDS
from regex_utils import WEEKDAY_SHORTNAMES
from regex_utils import MONTH_SHORTNAMES

from regex_utils import MDY_DATE_PATTERN
from regex_utils import IN_N_INTERVALS_PATTERN
from regex_utils import RELATIVE_WEEKDAY_PATTERN
from regex_utils import RELATIVE_INTERVAL_PATTERN
from regex_utils import QUICK_DAYS_PATTERN

from regex_utils import NUMBER_WORDS


class DateExpression:

    return_type: Type[date | timedelta] | None = None
    pattern: Pattern | None =  None

    @classmethod
    def members(cls):
        return (s for s in cls.__subclasses__())

    def __init__(self):
        pass

    def __init_subclass__(cls):
        if cls.pattern is None:
            raise NotImplementedError
        if cls.return_type is None:
            cls.return_type = date

        if not hasattr(cls, 'parse_match'):
            raise NotImplementedError

    def __repr__(self):
        pass

    def parse_match(self, m: Match):
        raise NotImplementedError



class Mdy_Expression(DateExpression):
    pattern = MDY_DATE_PATTERN 
    pass

    @classmethod
    def parse_match(cls, 

class Quick_Days_Expression:
    pattern = QUICK_DAYS_PATTERN





for m in DateExpression.members():
    print(m.return_type)
