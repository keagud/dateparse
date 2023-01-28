
from dateparse import DateParser
import datetime
from datetime import date


parser = DateParser(date.today())

#' a week from ' is getting dropped!
items = ["today", "tomorrow", "this friday", "a week from thursday"]

for i in items:
    print(parser.get_first(i))



exit()
def make_date(date_params):
    return datetime.date(*date_params)
  
with open("tests/params.yaml", "r") as infile:
    test_data = yaml.full_load(infile)

test_data_set:dict = test_data[0]



init_year: int = test_data_set["year"]
init_month: int = test_data_set["month"]
init_day: int = test_data_set["day"]

init_date = datetime.date(init_year, init_month, init_day)
parser = DateParser(current_date=init_date)

vals: dict = test_data_set["expected_base"]


