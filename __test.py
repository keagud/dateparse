from dateparse import DateParser


def pr(*args, **kwargs):
    dp = DateParser()
    s = dp.get_first(*args,**kwargs)
    print(s)
    return s

import ipdb; ipdb.set_trace()
pr("January 2")

