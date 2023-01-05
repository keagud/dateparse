from datetime import date, timedelta
from pprint import pformat
from typing import Iterable


import sys

import logging


from ._parse_util import DateMatch
from ._parse_util import DateGroups
from ._parse_util import AbsoluteDateExpression
from ._parse_util import DateDelta
from ._parse_util import date_expressions as defined_date_exprs


if len(sys.argv) > 1 and sys.argv[1].lower() == "--debug":
    logging.basicConfig(level=logging.DEBUG)


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

    def group_match_tokens(self, text: str) -> DateGroups:
        text = self.sub_named_days(text)
        return DateGroups(text, self.date_expressions)

    def parse_date_match(self, date_match: DateMatch) -> date | timedelta:
        return date_match.to_date(self.current_date)

    def parse_tokens(self, match_iter: Iterable[DateMatch]) -> date:

        """
        Takes an iterable consisting of an AbsoluteDateExpression
        preceeded by any number of DeltaDateExpressions

        Returns the date object representing the absolute expression + the sum of all deltas
        Any deltas that come after the absolute expression are ignored.
        """

        logging.debug(
            "\nENTERING PARSE_TOKENS WITH PARAMS: %s",
            pformat([m.content for m in match_iter]),
        )

        offset: list[DateDelta] = []
        anchor_date: date | None = None

        for match in match_iter:

            logging.debug("\ttoken: %s", match.content)
            if isinstance(match.expression, AbsoluteDateExpression):
                logging.debug("\tAnchor date: %s", match.content)
                anchor_date = match.to_date(self.current_date)
                break

            offset.append(match.to_date(self.current_date))

            logging.debug(
                "\tDelta: %s as %s",
                pformat(match.content),
                str(match.to_date(self.current_date)),
            )

        if anchor_date is None:
            raise ValueError(
                f"Unable to parse as a date: {' '.join([c.content for c in match_iter])}"
            )

        # determine the total amount of time to offset the anchor date
        # by summing all deltas
        total_offsets = {"day": 0, "month": 0, "year": 0}

        for delta in offset:
            for interval, count in vars(delta).items():
                if not interval in total_offsets:
                    continue
                total_offsets[interval] += count

        # add the delta sum to anchor for the final result

        parsed_date_values = {
            "day": anchor_date.day + total_offsets["day"],
            "month": anchor_date.month + total_offsets["month"],
            "year": anchor_date.year + total_offsets["year"],
        }

        if not 0 < parsed_date_values["month"] < 13:
            month_val = parsed_date_values["month"]
            adjusted_month = ((month_val - 1) % 12) + 1
            year_offset = (month_val - 1) // 12

            parsed_date_values["month"] = adjusted_month
            parsed_date_values["year"] += year_offset

        parsed_date = date(**parsed_date_values)

        if parsed_date < self.current_date:
            parsed_date = parsed_date.replace(year=self.current_date.year + 1)

        return parsed_date

    def extract_and_parse(self, text: str) -> date:
        """
        Main wrapper method for converting a complex string expression to a datetime.date object.
        Input: text as a string
        Output: datetime.date object
        If no known date format patterns are matched, raises a ValueError
        """

        groups = self.group_match_tokens(text).get_groups()

        if not groups:
            raise ValueError(
                f"Could not match against any date expression types: {text}"
            )

        last_expr_tokens = groups[-1]

        return self.parse_tokens(last_expr_tokens)
