import re


class DateRegex:

    Date_Formats = {"ISO": "%Y-%m-%d"}

    months_short = [
        "",
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]  # one-indexed so that numeric month value is the same as the index

    weekdays_short = [
        "",
        "mon",
        "tue",
        "wed",
        "thu",
        "fri",
        "sat",
        "sun",
    ]  # one-indexed for symmetry with months_short[] mostly

    named_days = {
        "christmas": "dec 25",
        "new years": "jan 1",
        "halloween": "oct 31",
    }  # TODO allow user to add to this
    # also TODO let this be used in the parser- currently it does not

    time_intervals = ["day", "week", "month", "year"]

    negative_interval_words = ["before"]
    positive_interval_words = ["from", "after"]

    number_words = [
        "",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
    ]

    # class-internal utility function to convert a list of strings to a
    # regex pattern string matching any element in the list
    # returned as a string rather than re.Pattern to allow further recombination
    def __list_to_regex(self, input_list: list) -> str:
        return "|".join([s for s in input_list if s])

    def __init__(self, named_days: dict[str, str] | None = None) -> None:

        # make regex pattern strings
        self.months_match_regex = self.__list_to_regex(self.months_short)
        self.weekday_match_regex = self.__list_to_regex(self.weekdays_short)
        self.time_interval_regex = self.__list_to_regex(self.time_intervals)
        self.number_words_regex = self.__list_to_regex(self.number_words)
        self.interval_preposition_regex = (
            self.__list_to_regex(self.positive_interval_words)
            + "|"
            + self.__list_to_regex(self.negative_interval_words)
        )

        # if additional named days beyond the defaults were specified, include those
        if named_days is not None:
            self.named_days.update(named_days)


        self.named_days_regex = self.__list_to_regex(list(self.named_days.keys()))

        # compile patterns

        # of the form "oct 20" "october 20" "10-20-2023
        self.date_pattern = re.compile(
            r"(" + self.months_match_regex + r"|\d+)[^\d\n]+?(\d{1,2})([^\d\n]+\d{4})?"
        )

        # phrases of the form "a week from"
        self.relative_interval_pattern = re.compile(
            r"(a\s*|"
            + self.number_words_regex
            + r")?\s*("
            + self.time_interval_regex
            + r")\w*[^\n\d\w]*("
            + self.interval_preposition_regex
            + ")"
        )

        # phrases of the form "in ten days", "in two weeks"
        self.in_n_intervals_pattern = re.compile(
            r"in[^\n\d\w](\w+|a)[^\n\d\w](" + self.time_interval_regex + r")\w*?"
        )

        # phrases of the form "this sunday", "next wednesday"
        self.relative_weekday_pattern = re.compile(
            r"(this|next)?[^\n\d\w]*(" + self.weekday_match_regex + ")"
        )

        # special dates like "christmas"
        # plus dates passed in at init time
        self.named_days_pattern = re.compile(r"(" + self.named_days_regex + ")")

        # collects the patterns refering to absolute dates
        # e.g. dates that are associated unambiguously with a datetime.date expression
        # these expressions are used by the parser to "anchor" any other time expressions to a date
        self.absolute_date_patterns = [
            self.date_pattern,
            self.in_n_intervals_pattern,
            self.relative_weekday_pattern,
            self.named_days_pattern,
        ]
