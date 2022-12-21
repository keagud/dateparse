import re
import datetime
from datetime import timedelta
from itertools import chain
import functools,typing


#
class DateParser:

    # CLASS PROPERTIES
    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    months: dict[str, tuple[int, int]] = {
        "january": (1, 30),
        "february": (2, 28),
        "march": (3, 31),
        "april": (4, 30),
        "may": (5, 31),
        "june": (6, 30),
        "july": (7, 31),
        "august": (8, 31),
        "september": (9, 30),
        "october": (10, 31),
        "november": (11, 30),
        "december": (12, 31),
    }

    default_named_days: dict[str, str] = {
        "christmas": "december 25",
        "halloween": "october 31",
    }

    named_intervals = {"week": 7, "year": 365}

    regex_list:typing.Callable = lambda ls, n: re.compile("|".join((x[:n] for x in ls)))




    # make regex patterns from months, weekdays, and named days
    def make_regex(self):
        
        regex_list:typing.Callable = lambda ls, n: re.compile("|".join((x[:n] for x in ls)))
        self.month_regex = regex_list(self.months,3)
        self.weekday_regex = regex_list(self.weekdays, 3)
        self.named_days_regex = regex_list(self.named_days, None)


    # constructor takes 2 optional args:
    # date to count as "today" (defaults to datetime.date.today())
    # additional named dates like holidays (defaults to none, only using the class-level named days)
    def __init__(
        self,
        date: datetime.date | None = None,
        named_days: dict[str, str] | None = None,
    ) -> None:
        self.date = date if date is not None else datetime.date.today()

        self.named_days = self.default_named_days

        if named_days is not None:
            self.named_days.update(named_days)

        self.make_regex()



    # converts an absolute date expression like "march 18" to a datetime.date
    def parse_absolute_date(self, date_expr: str)-> datetime.date | None:
        pass


    def get_date_anchor(self, str_input: str) -> datetime.date:  # type:ignore
        """
        Get the date object for the "anchor date" of the given complex time expression
        Ex:
            "Four days before march 8" -> 2022-03-08
            "A week from next wednesday" -> [date of next wednesday].
        """


        anchor_iter = chain.from_iterable(
            [
                re.finditer(p, str_input)
                for p in (self.weekday_regex, self.month_regex, self.named_days_regex)
            ]
        )

        cmp = lambda a,b: b if a is None or b.end() > a.end() else a

        #get the last (rightmost) match
        a = functools.reduce(cmp, anchor_iter)
        print(a)


        
        

        rightmost:re.Match|None = None
        rightpos = 0

        for match in anchor_iter:
            if match and match.end() > rightpos:
                pass


    def get_months_interval(
        self, months_count: int, start_date: datetime.date | None = None  # type:ignore
    ) -> int:  # type:ignore

        """
        Converts expressions like "3 months" into an equivalant number of days
        This is needed to account for different months having different numbers of days.

        """
        start_date = self.date if start_date is None else start_date
        pass

    # use async maybe?
    def parse_interval(self, interval_str: str) -> timedelta:  # type:ignore
        """
        Converts an interval expression to a timedelta (expressing the difference in days)
        Ex:
            "A week before" -> -7 days
            "Six weeks after" -> +42 days
        """
        pass

    def parse_date(self, date_expr: str, base_date: datetime.date | None = None) -> datetime.date:  # type: ignore

        base_date = self.date if base_date is None else base_date
        pass


