import pytest

from toolkit.ledger.money import (
    MoneyError,
    allocate,
    format_money,
    minor_digits,
    parse_money,
    split_evenly,
)


# --- minor_digits -------------------------------------------------------


def test_minor_digits_of_two_digit_currencies():
    assert [minor_digits(code) for code in ["USD", "EUR", "GBP", "CNY"]] == [2, 2, 2, 2]


def test_minor_digits_result_is_an_int():
    assert type(minor_digits("USD")) is int


# --- parse_money --------------------------------------------------------


def test_parse_money_amount_in_minor_units():
    assert parse_money("12.34 USD") == (1234, "USD")


def test_parse_money_fewer_decimals_than_minor_digits():
    assert parse_money("12.5 EUR") == (1250, "EUR")


def test_parse_money_negative_amount():
    assert parse_money("-7.05 EUR") == (-705, "EUR")


def test_parse_money_three_digit_currency():
    assert parse_money("1.5 KWD") == (1500, "KWD")
    assert parse_money("0.005 BHD") == (5, "BHD")


def test_parse_money_ungrouped_long_number():
    assert parse_money("1234567.89 USD") == (123456789, "USD")


def test_parse_money_rounds_negative_half_away_from_zero():
    assert parse_money("-0.125 USD") == (-13, "USD")


def test_parse_money_half_is_not_rounded_to_even():
    assert parse_money("0.105 USD") == (11, "USD")
    assert parse_money("0.115 USD") == (12, "USD")
    assert parse_money("2.5 JPY") == (3, "JPY")
    assert parse_money("3.5 JPY") == (4, "JPY")


def test_parse_money_rounding_looks_at_all_extra_digits():
    assert parse_money("0.12499999 USD") == (12, "USD")
    assert parse_money("0.4999 JPY") == (0, "JPY")


def test_parse_money_empty_text_raises_money_error():
    with pytest.raises(MoneyError):
        parse_money("")


def test_parse_money_unknown_code_raises_money_error():
    with pytest.raises(MoneyError):
        parse_money("12.34 XXX")


def test_parse_money_trailing_dot_raises_money_error():
    with pytest.raises(MoneyError):
        parse_money("5. USD")


def test_parse_money_comma_in_fraction_raises_money_error():
    with pytest.raises(MoneyError):
        parse_money("1.234,5 USD")


def test_parse_money_currency_symbol_raises_money_error():
    with pytest.raises(MoneyError):
        parse_money("$5 USD")


def test_parse_money_error_is_a_value_error():
    with pytest.raises(ValueError):
        parse_money("five dollars")


# --- format_money -------------------------------------------------------


def test_format_money_zero():
    assert format_money(0, "USD") == "0.00 USD"


def test_format_money_zero_digit_currency_has_no_dot():
    assert format_money(1500, "JPY") == "1500 JPY"
    assert format_money(0, "KRW") == "0 KRW"


def test_format_money_grouping_of_the_major_part():
    assert format_money(123456789, "EUR", grouping=True) == "1,234,567.89 EUR"


def test_format_money_unknown_currency_raises_money_error():
    with pytest.raises(MoneyError):
        format_money(100, "XXX")


def test_format_money_string_amount_raises_type_error():
    with pytest.raises(TypeError):
        format_money("100", "USD")


# --- allocate -----------------------------------------------------------


def test_allocate_result_is_a_list_of_ints():
    result = allocate(100, (1, 1))
    assert type(result) is list and all(type(part) is int for part in result)


def test_allocate_largest_remainder_gets_the_extra_unit():
    assert allocate(101, [1, 1, 2]) == [25, 25, 51]


def test_allocate_several_extra_units_by_descending_remainder():
    assert allocate(100, [1, 3, 3]) == [14, 43, 43]
    assert allocate(11, [2, 3, 2]) == [3, 5, 3]


def test_allocate_amount_smaller_than_number_of_parts():
    assert allocate(1, [1, 1, 1]) == [1, 0, 0]
    assert allocate(2, [1, 1, 1]) == [1, 1, 0]


def test_allocate_single_ratio_gets_everything():
    assert allocate(123, [5]) == [123]


def test_allocate_empty_ratios_raise_money_error():
    with pytest.raises(MoneyError):
        allocate(100, [])


def test_allocate_does_not_modify_the_ratios():
    ratios = [3, 2, 1]
    allocate(10, ratios)
    assert ratios == [3, 2, 1]


# --- split_evenly -------------------------------------------------------


def test_split_evenly_single_part():
    assert split_evenly(5, 1) == [5]


def test_split_evenly_negative_parts_raise_money_error():
    with pytest.raises(MoneyError):
        split_evenly(100, parts=-1)
