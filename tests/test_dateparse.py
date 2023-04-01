import datetime

import pytest
import yaml

from dateparse import DateParser

with open("tests/params.yaml", "r") as infile:
    test_data = yaml.full_load(infile)


def make_date(date_params):
    return datetime.date(*date_params)


@pytest.fixture(params=test_data)
def make_parser_group(request):
    test_data_set: dict = request.param

    init_year: int = test_data_set["year"]
    init_month: int = test_data_set["month"]
    init_day: int = test_data_set["day"]

    init_date = datetime.date(init_year, init_month, init_day)
    test_parser = DateParser(base_date=init_date)

    test_io_vals: dict = test_data_set["expected_base"]
    return test_parser, test_io_vals


def test_parser(make_parser_group):
    parser, vals = make_parser_group

    for input_text, test_date_vals in vals.items():
        test_date = datetime.date(*test_date_vals)

        first_date_tuple = parser.get_first(input_text)
        last_date_tuple = parser.get_last(input_text)

        first_date = parser.get_first_date(input_text)
        last_date = parser.get_last_date(input_text)

        assert first_date_tuple.date == test_date
        assert last_date_tuple.date == test_date
        assert first_date == test_date
        assert last_date == test_date


def test_multiple_expressions(make_parser_group):
    parser, vals = make_parser_group

    inputs = []
    expected_dates = []

    for expr, date_value in vals.items():
        inputs.append(expr)
        expected_dates.append(make_date(date_value))

    input_text = " ".join(inputs)

    iter_parser = parser.get_all(input_text)

    for inp, outp in zip(expected_dates, iter_parser):
        assert inp == outp.date

    iter_date_parser = parser.get_all_dates(input_text)

    for inp, outp in zip(expected_dates, iter_date_parser):
        assert inp == outp


def test_error_handling(make_parser_group):
    parser, vals = make_parser_group

    bad_inputs = ["foo", "bar", "維基百科", "O! the pelican!", "شكشوكة"]

    for text in bad_inputs:
        assert parser.get_last(text) is None
        assert parser.get_first(text) is None

        assert parser.get_last_date(text) is None
        assert parser.get_first_date(text) is None
