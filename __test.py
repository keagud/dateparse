
from dateparse.parsefunctions import absolute_patterns
from dateparse.parsefunctions import relative_patterns

import datetime
from dateparse.parseutil import DateTuple, _match_to_tuple, _extract_regex_matches, basic_parse
from dateparse.parseutil import preprocess_input

test_inputs = ["A week from today", "Ten days from today", "January 2"]

for t in test_inputs:
    s = basic_parse(datetime.date.today(), t)
    print(s)



