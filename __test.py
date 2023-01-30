
from dateparse.parsefunctions import absolute_patterns
from dateparse.parsefunctions import relative_patterns


pset = absolute_patterns + relative_patterns
from dateparse.parseutil import DateTuple, _match_to_tuple, _extract_regex_matches

test_inputs = ["A week from today", "Ten days from today", "January 2"]

for t in test_inputs:
    t = t.lower()
    x = _extract_regex_matches(t, pset)

    for i in x:
        print(i)
    print("DONE")



