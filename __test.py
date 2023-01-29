from dateparse import DateParser


def pr(*args, **kwargs):
    dp = DateParser()
    s = dp.get_first(*args,**kwargs)
    print(s)
    return s

import pdb; pdb.set_trace()
pr("January 2")

