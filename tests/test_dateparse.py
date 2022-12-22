import pytest, yaml, datetime

from dateparse.dateparse import DateParser

with open("testing_setup.yaml", "r") as infile:
    test_data = yaml.full_load(infile)
    print("Loaded test values from testing_setup.yaml")

@pytest.fixture(params=test_data)
def make_parser(request):
    d = request.param

    year:int = d["year"]
    month:int = d["month"]
    day: int = d["day"]

    test_date = datetime.date(year,month,day)
    return DateParser(test_date)



def test_parser(make_parser):

    tests:dict = test_data[0]["expected_base"]

    for text, vals in tests.items():
      test_date=   datetime.date(vals[0], vals[1], vals[2])

      assert make_parser.parse_date(text) == test_date
