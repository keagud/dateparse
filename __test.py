from dateparse import DateParser


def pr(*args, **kwargs):
    dp = DateParser()
    s = dp.get_first(*args,**kwargs)
    print(s)
    return s

pr(" a week from thurs")

