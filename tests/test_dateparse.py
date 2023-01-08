import pytest, yaml, datetime

from dateparse import DateParser
from collections import namedtuple


with open("tests/params.yaml", "r") as infile:
    test_data = yaml.full_load(infile)


@pytest.fixture(params=test_data)
def make_parser_group(request):
    test_data_set: dict = request.param

    init_year: int = test_data_set["year"]
    init_month: int = test_data_set["month"]
    init_day: int = test_data_set["day"]

    init_date = datetime.date(init_year, init_month, init_day)
    test_parser = DateParser(current_date=init_date)

    test_io_vals: dict = test_data_set["expected_base"]
    return test_parser, test_io_vals


def test_parser(make_parser_group):
    parser, vals = make_parser_group

    for input_text, test_date_vals in vals.items():
        test_date = datetime.date(*test_date_vals)

        assert parser.get_last(input_text) == test_date
