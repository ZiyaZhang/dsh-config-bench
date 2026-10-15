from fractions import Fraction

import pytest

from toolkit.numfmt.grouping import (
    GroupingError,
    format_grouped,
    parse_grouped,
    round_exact,
)


# --- round_exact --------------------------------------------------------


def test_round_exact_result_is_a_fraction():
    result = round_exact(3)
    assert type(result) is Fraction and result == 3


def test_round_exact_half_even_goes_to_the_even_neighbour():
    assert round_exact(0.5) == 0
    assert round_exact(1.5) == 2
    assert round_exact(2.5) == 2
    assert round_exact(3.5) == 4


def test_round_exact_half_even_of_negative_value():
    assert round_exact(-2.5) == -2
    assert round_exact(-3.5) == -4


def test_round_exact_fraction_tie_with_half_even():
    assert round_exact(Fraction(2675, 1000), 2) == Fraction(268, 100)
    assert round_exact(Fraction(2665, 1000), 2) == Fraction(266, 100)


def test_round_exact_negative_decimals_round_to_tens_and_hundreds():
    assert round_exact(1234, -2) == 1200
    assert round_exact(1250, -2) == 1200
    assert round_exact(1350, -2) == 1400
    assert round_exact(1250, -2, "half-up") == 1300
    assert round_exact(15, -1) == 20


def test_round_exact_huge_number_keeps_all_digits():
    value = 10 ** 30 + Fraction(5, 8)
    assert round_exact(value, 1) == 10 ** 30 + Fraction(6, 10)


def test_round_exact_bool_raises_type_error():
    with pytest.raises(TypeError):
        round_exact(True)


# --- format_grouped -----------------------------------------------------


def test_format_grouped_groups_thousands_and_keeps_two_decimals():
    assert format_grouped(1234567.891) == "1,234,567.89"


def test_format_grouped_group_sizes():
    assert format_grouped(12345, 0) == "12,345"
    assert format_grouped(123456, 0) == "123,456"
    assert format_grouped(1234567, 0) == "1,234,567"


def test_format_grouped_half_even_is_the_default():
    assert format_grouped(1234.5, 0) == "1,234"
    assert format_grouped(1235.5, 0) == "1,236"
    assert format_grouped(0.125) == "0.12"


def test_format_grouped_fraction_exactly_on_the_tie():
    assert format_grouped(Fraction(2675, 1000)) == "2.68"
    assert format_grouped(Fraction(2665, 1000)) == "2.66"
    assert format_grouped(Fraction(2665, 1000), rounding="half-up") == "2.67"


def test_format_grouped_rounding_can_add_a_digit_and_a_group():
    assert format_grouped(999.9951) == "1,000.00"
    assert format_grouped(999999.5, 0, "half-up") == "1,000,000"


def test_format_grouped_empty_separator_means_no_grouping():
    assert format_grouped(1234567.5, sep="") == "1234567.50"


def test_format_grouped_small_float_is_not_written_with_an_exponent():
    assert format_grouped(1.5e-7, 8) == "0.00000015"


def test_format_grouped_integer_input():
    assert format_grouped(-1000000) == "-1,000,000.00"


def test_format_grouped_unknown_separator_raises_value_error():
    with pytest.raises(ValueError):
        format_grouped(1, sep=";")


def test_format_grouped_string_raises_type_error():
    with pytest.raises(TypeError):
        format_grouped("1234.5")


# --- parse_grouped ------------------------------------------------------


def test_parse_grouped_whole_number_is_a_fraction_too():
    result = parse_grouped("1,234")
    assert type(result) is Fraction and result == 1234


def test_parse_grouped_signs():
    assert parse_grouped("-1,000") == -1000
    assert parse_grouped("+1,000") == 1000
    assert parse_grouped("-0.50") == Fraction(-1, 2)


def test_parse_grouped_other_separator_and_point():
    assert parse_grouped("1.234.567,5", sep=".", point=",") == Fraction(2469135, 2)


def test_parse_grouped_empty_separator_accepts_only_plain_digits():
    assert parse_grouped("1234.5", sep="") == Fraction(2469, 2)
    with pytest.raises(GroupingError):
        parse_grouped("1,234", sep="")


def test_parse_grouped_group_of_four_digits_raises():
    with pytest.raises(GroupingError):
        parse_grouped("1,2345")


def test_parse_grouped_two_separators_in_a_row_raise():
    with pytest.raises(GroupingError):
        parse_grouped("1,,234")


def test_parse_grouped_empty_text_raises():
    with pytest.raises(GroupingError):
        parse_grouped("")


def test_parse_grouped_two_signs_raise():
    with pytest.raises(GroupingError):
        parse_grouped("--1")


def test_parse_grouped_grouping_error_is_a_value_error():
    with pytest.raises(ValueError):
        parse_grouped("abc")


