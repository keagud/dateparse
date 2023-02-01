Dateparse
===========

A python library for parsing natural language time descriptions. 

Installation
-------------
Dateparse is on PyPi; install with Pip: :code:`$ pip install dateparse`

Usage
------ 
>>> import dateparse
>>> from datetime import date

>>> # The main use case is extracting a single date from a string
>>> dateparse.basic_parse(date.today(), "a week from friday")
DateResult(date=datetime.date(2023, 2, 10), start=0, end=15, content='a week from fri')

>>> # by default the first (leftmost) encountered date is returned
>>> dateparse.basic_parse(date.today(), "a week from thursday and a week from friday")
DateResult(date=datetime.date(2023, 2, 9), start=0, end=15, content='a week from thu') 

>>> # the from_right option changes this
>>> dateparse.get_first(date.today(), "a week from thursday and a week from friday")
DateResult(date=datetime.date(2023, 2, 10), start=0, end=15, content='a week from fri')

>>> # default behavior for all parse functions is to get the next future date matching the expression
>>> # relative to the given base date
>>> # this can be changed with the allow_past option
>>> dateparse.basic_parse(date(1970, 9, 8), "january 1", allow_past=True)
DateResult(date=datetime.date(1970, 1, 1), start=0, end=9, content=' january 1')

>>> # parse_all gets all expressions in a list
>>> dateparse.parse_all(date.today(), "a week from thursday and four days before march 11")
[DateResult(date=datetime.date(2023, 2, 9), start=0, end=15, content='a week from thu'), DateResult(date=datetime.date(2023, 3, 7), start=24, end=50, content='four days before march 11')]

>>> # the default return type for dates is a DateResult, a simple named tuple containing the date's info
>>> # For convenience, there are also functions to just get the date
>>> dateparse.basic_date_parse(date.today(), "february 9")
datetime.date(2023, 2, 9)

>>> # parse_all_dates works in the same way
>>> # a DateParser object holds a specified baseline date 
>>> # by default, assumes the baseline date is date.today()
>>> parser = dateparse.DateParser() 

>>> # parses dates with a reference point of january 17, 2021 
>>> parser_january = dateparse.DateParser(base_date = date(2021, 17, 1)) 

>>> # DateParser also supports named days by default
>>> parser.get_first("four days after halloween 2024")
DateResult(date=datetime.date(2024, 11, 4), start=0, end=31, content='four days after october 31 2024')

>>> # You can also define your own custom named days as a string dictionary and pass it into the parser
>>> my_dates = {'my birthday' : 'june 11'}
>>> my_parser = dateparse.DateParser(named_days = my_dates)
>>> my_parser.get_first("a month before my birthday")
DateResult(date=datetime.date(2023, 5, 14), start=0, end=22, content='a month before june 11')

>>> # DateParser.get_first and DateParser.get_last are convenience wrappers around basic_parse
>>> # to get the first or last expression, with the base date defined at initialization
>>> my_parser.get_first("a week from thurs and two months after friday")
DateResult(date=datetime.date(2023, 2, 9), start=0, end=15, content='a week from thu')
>>> my_parser.get_last("a week from thurs and two months after friday")
DateResult(date=datetime.date(2023, 4, 3), start=21, end=42, content='two months after fri')

>>> # DateParser.get_all and DateParser.get_all_dates wrap parse_all and parse_all_dates
>>> my_parser.get_all("a week from thurs and two months after friday")
[DateResult(date=datetime.date(2023, 2, 9), start=0, end=15, content='a week from thu'), DateResult(date=datetime.date(2023, 4, 3), start=21, end=42, content='two months after fri')]
>>> my_parser.get_all_dates("a week from thurs and two months after friday")
[datetime.date(2023, 2, 9), datetime.date(2023, 4, 3)]


Other Info
----------
**This project is under active development.** The core API is unlikely to change much at this point, but the under-the-hood details are still very much in flux. 

Dateparse requires Python 3.10 or higher, thanks the author's neurotic devotion to type annotations. 
