from datetime import date
from pprint import pprint

from dateparse import DateParser

dp = DateParser()

t = date.today()
# ipdb.set_trace()
s = dp.get_last("a month after three days before today")
pprint(s)
print(s.date)
