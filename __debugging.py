
from dateparse import DateParser
import yaml
import datetime


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



inputs = []
expected_dates = []

for expr, date_value in vals.items():
    inputs.append(expr)
    expected_dates.append(make_date(date_value))

input_text = " ".join(inputs)



iter_parser = parser.extract_and_parse(input_text)

c = 0
for expected, received in zip(inputs, iter_parser):
    c += 1

    print(f"\nexpected: {expected} | got: {received}\n")
    import pdb; pdb.set_trace()

print(f"{len(inputs)} expressions expected, got {c}")




