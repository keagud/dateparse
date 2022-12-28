import re
from datetime import date, timedelta


from regex_utils import date_patterns, iter_all_matches


class DateParser:

    default_named_days = {"christmas": "december 25", "halloween": "october 31"}

    def __init__(
        self, current_date: date | None = None, named_days: dict[str, str] | None = None
    ) -> None:

        self.current_date = current_date if current_date is not None else date.today()

        self.named_days = self.default_named_days

        if named_days is not None:
            self.named_days.update(named_days)
