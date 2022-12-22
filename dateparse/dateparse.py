import re
import datetime
from datetime import timedelta
from itertools import chain
import functools

from .date_regexes import DateRegex


#


class DateParser:
    def __init__(
        self,
        date: datetime.date | None = None,
        named_days: dict[str, str] | None = None,
        regex_defs: DateRegex | None = None,
    ) -> None:
        self.date = date if date is not None else datetime.date.today()

        # define a DateRegex object if one was not specified
        # pass the new object the user-defined named days to include in its patterns
        self.regexes = (
            regex_defs if regex_defs is not None else DateRegex(named_days=named_days)
        )

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
                for p in (
                    self.regexes.weekday_match_regex,
                    self.regexes.months_match_regex,
                    self.regexes.named_days_regex,  
                )
            ]
        )

        cmp = lambda a, b: b if a is None or b.end() > a.end() else a

        # get the last (rightmost) match
        a = functools.reduce(cmp, anchor_iter)
        print(a)

        rightmost: re.Match | None = None
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

    # removes all non-digit characters from input
    def clean_whitespace(self, input_str: str) -> str:
        return re.sub(r"\D", "", input_str)

    # calls clean_whitespace() on input str
    # then casts to int before returning
    def clean_and_cast(self, input_str: str) -> int:
        try:
            clean_str = self.clean_whitespace(input_str)
            return int(clean_str)
        except Exception as e:

            raise Exception("Unable to read as a number: {}".format(input_str))

    def read_number(self, input_str: str) -> int:
        if input_str.isdigit():
            return int(input_str)

        if input_str.lower() in self.regexes.number_words:
            return self.regexes.number_words.index(input_str.lower())

        raise Exception("Tried to parse as a number and failed: {}".format(input_str))

    # normalizes time interval terms to days
    # "week" -> 7, etc
    def normalize_interval_to_days(self, input_str: str) -> int:

        match input_str:
            case "day":
                days_count_multiplier = 1
            case "week":
                days_count_multiplier = 7

            case "month":
                # TODO this should take into account that months have variable number of days
                days_count_multiplier = 30
            case "year":
                # TODO same here
                # what these should both do is advance/decrement the month or year field in the final output by n
                days_count_multiplier = 365
            case _:
                raise Exception("Unknown interval type: {}".format(input_str))

        return days_count_multiplier

    # takes a string of the form "<n> <days/weeks/months/years> (from)"
    # returns a Timedelta object representing that amount of time

    def get_interval(self, input_str: str) -> timedelta:
        input_str = input_str.lower()
        interval_pattern_match = re.search(
            self.regexes.relative_interval_pattern, input_str
        )

        if not interval_pattern_match:
            raise LookupError("Unrecognized interval: '{}'".format(input_str))

        # unpack the matched interval phrase
        count_str, interval_type, preposition = interval_pattern_match.groups(
            default="one"
        )

        days_count_multiplier = 0  # factor for converting input to a number of days
        # e.g. if the input is "week", days_count_multiplier is 7, etc

        intervals_count = 1

        if count_str in self.regexes.number_words:
            intervals_count = self.regexes.number_words.index(count_str)
        elif count_str.isdigit():
            intervals_count = int(count_str)

        days_count_multiplier = self.normalize_interval_to_days(interval_type)

        # a "positive" modifier means we should add the timedelta to the main date- it happens after
        # a "negative" modifier means we should subtract- it happens before
        preposition_modifier = (
            1 if preposition in self.regexes.positive_interval_words else -1
        )

        days_delta = preposition_modifier * (days_count_multiplier * intervals_count)

        return timedelta(days=days_delta)

    # determines if input is a valid absolute date (i.e. can be translated into ISO format)
    # if so, returns a match object representing it
    # this is the case if the input is in one of these forms:
    #   "this/next <weekday>"
    #   "in <n> <days/weeks/months/years>"
    #   a special predefined date (e.g. "christmas")

    def get_date_match(self, input_str: str) -> re.Match[str]:

        matches: list[re.Match[str] | None] = [
            re.search(d, input_str) for d in self.regexes.absolute_date_patterns
        ]

        if not any(matches):
            raise ValueError(
                "'{}' did not match against any known date patterns".format(input_str)
            )

        return [m for m in matches if m][0]

    # converts string input into a Date object
    # possible inputs:
    #   sept 11
    #   9/11
    #   9-11
    #   september 11
    # if a year is included, it must be last
    # if no  year is included, assumed to be the next occurrence of that date

    def get_absolute_date(self, input_str: str, allow_past_dates=True) -> datetime.date:
        input_str = input_str.lower()

        date_match = re.search(self.regexes.date_pattern, input_str)

        if not date_match:

            raise Exception(
                'Unable to parse input: "{}" does not match a recognized date pattern'.format(
                    input_str
                )
            )

        current_date = datetime.date.today()

        current_year = current_date.year

        date_fields = date_match.groups(default=str(current_year))

        month_match, day_match, year_match = [item for item in date_fields]

        if month_match in self.regexes.months_short:
            month_match = self.regexes.months_short.index(month_match)
        else:
            month_match = self.clean_and_cast(month_match)

        day_match = self.clean_and_cast(day_match)
        year_match = self.clean_and_cast(year_match)

        # see if the date as currently calculated is in the past
        # and if that's not allowed, correct it
        date_in_past = (
            current_date.toordinal()
            > datetime.date(year_match, month_match, day_match).toordinal()
        )

        if date_in_past and not allow_past_dates:
            year_match = current_year + 1

        return datetime.date(year_match, month_match, day_match)

    # takes a weekday as a string, returns the date of its next occurrence relative to today
    # can also handle phrases like "this tuesday", "next tuesday"

    def get_weekday_date(
        self, input_str: str, today: datetime.date = datetime.date.today()
    ) -> datetime.date:
        input_str = input_str.lower()
        weekday_match = re.search(self.regexes.relative_weekday_pattern, input_str)
        if not weekday_match:
            raise Exception(
                'Parse error: tried to read "{}" as a weekday name and failed'.format(
                    input_str
                )
            )

        modifier, weekday = weekday_match.groups(default="this")

        weekday_index = self.regexes.weekdays_short.index(weekday)
        today_weekday = today.isoweekday()
        weekday_diff = weekday_index - today_weekday

        if weekday_diff < 0:
            weekday_diff = weekday_diff + 7

        if modifier == "next":
            weekday_diff = weekday_diff + 7

        return today + timedelta(days=weekday_diff)

    def get_countdown_type_date(
        self, input_str: str, today: datetime.date = datetime.date.today()
    ) -> datetime.date:

        countdown_match = re.search(self.regexes.in_n_intervals_pattern, input_str)

        if not countdown_match:
            raise Exception(
                'Parse error: tried to read "{}" as a "countdown interval" and failed'.format(
                    input_str
                )
            )

        count, interval_type = countdown_match.groups()

        count_num = self.read_number(count)

        days = self.normalize_interval_to_days(interval_type)

        delta = timedelta(days=(days * count_num))

        return today + delta

    # general purpose function for parsing a date
    # checks if the string is a match in any of the patterns in absolute_date_patterns[]
    # and calls the appropriate parse function

    def parse_date(
        self,
        input_str: str,
        allow_past_dates: bool = True,
        pattern: re.Pattern | None = None,
    ) -> datetime.date:
        input_str = input_str.lower()

        # if it's just 'today' or 'tomorrow', we don't need to go through the rest of the rigamarole
        # TODO this could prolly be refactored better

        if input_str == "today":
            return datetime.date.today()
        elif input_str == "tomorrow":
            return datetime.date.today() + timedelta(days=1)

        selected_pattern = None

        if pattern:
            selected_pattern = pattern
        else:

            selected_pattern = None
            for pattern in self.regexes.absolute_date_patterns:
                if re.search(pattern, input_str):
                    selected_pattern = pattern

        if not selected_pattern in self.regexes.absolute_date_patterns:
            raise Exception(
                """Parse error: "{}" does not match any known date patterns
                {} pattern was applied without success""".format(
                    input_str, pattern
                )
            )

        selected_pattern_str = str(selected_pattern)

        if selected_pattern_str == str(self.regexes.date_pattern):
            return self.get_absolute_date(input_str, allow_past_dates)
        elif selected_pattern_str == str(self.regexes.relative_weekday_pattern):
            return self.get_weekday_date(input_str)
        elif selected_pattern_str == str(self.regexes.in_n_intervals_pattern):
            return self.get_countdown_type_date(input_str)

        else:
            raise Exception(
                'Parse error: unable to apply pattern "{}" to parse string "{}"'.format(
                    selected_pattern, input_str
                )
            )

    def parse_complex_date(
        self, input_str: str, allow_past_dates=True
    ) -> datetime.date:

        # the "anchor date" is the absolute date to which modifiers like "before/after" are applied
        # such a date is always representable by a datetime.date object
        anchor_date_match = self.get_date_match(input_str)

        if not anchor_date_match:
            raise Exception('Unable to begin parsing for "{}"'.format(input_str))

        anchor_date = self.parse_date(anchor_date_match.group())

        parsing_str = input_str[
            : anchor_date_match.start()
        ]  #'slice off' the bit of string with the anchor date
        date_offset = timedelta(days=0)

        # I can't believe it's not scanf()!
        # works by parsing sucessive substrings that match relative_interval_pattern
        #   i.e. substrings of the form '<n> <time unit(s)> <before/after etc>'
        # calls get_interval to get a Timedelta, which is added to date_offset
        # when there's nothing left to parse, add date_offset to anchor_date and return it!

        # TODO make this use an iterator instead of this jank
        while len(parsing_str) > 1:

            next_interval = self.get_interval(parsing_str)
            if not next_interval:
                break

            date_offset = date_offset + next_interval
            interval_match = re.search(
                self.regexes.relative_interval_pattern, parsing_str
            )
            parsing_str = parsing_str[: interval_match.start()]

        parsed_date = anchor_date + date_offset
        return parsed_date
