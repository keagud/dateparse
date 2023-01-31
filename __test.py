import datetime
from dateparse.parseutil import basic_parse

test_inputs = ["A week from today", "Ten days from today", "January 2"]

for t in test_inputs:
    s = basic_parse(datetime.date.today(), t)
    if s is not None:
        print(s.date)
