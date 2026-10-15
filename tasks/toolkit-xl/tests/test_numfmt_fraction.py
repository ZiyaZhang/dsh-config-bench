from fractions import Fraction

import pytest

from toolkit.numfmt.fraction import (
    FractionError,
    format_mixed,
    format_repeating,
    parse_mixed,
    parse_repeating,
)


# --- format_mixed -------------------------------------------------------


def test_format_mixed_improper_fraction_becomes_mixed():
    assert format_mixed(Fraction(7, 3)) == "2 1/3"


def test_format_mixed_int_input():
    assert format_mixed(5) == "5"
    assert format_mixed(-12) == "-12"


def test_format_mixed_negative_mixed_number_truncates_toward_zero():
    assert format_mixed(Fraction(-7, 3)) == "-2 1/3"


def test_format_mixed_large_parts():
    assert format_mixed(Fraction(1000001, 1000)) == "1000 1/1000"


# --- parse_mixed --------------------------------------------------------


def test_parse_mixed_mixed_fraction():
    result = parse_mixed("2 1/3")
    assert type(result) is Fraction and result == Fraction(7, 3)


def test_parse_mixed_sign_applies_to_the_whole_number():
    assert parse_mixed("-2 1/3") == Fraction(-7, 3)


def test_parse_mixed_plus_sign():
    assert parse_mixed("+7/3") == Fraction(7, 3)
    assert parse_mixed("+1 1/2") == Fraction(3, 2)


def test_parse_mixed_zero_numerator():
    assert parse_mixed("0/5") == 0
    assert parse_mixed("3 0/5") == 3


def test_parse_mixed_leading_zeros():
    assert parse_mixed("007 01/02") == Fraction(15, 2)


def test_parse_mixed_sign_inside_raises():
    with pytest.raises(FractionError):
        parse_mixed("2 -1/3")
    with pytest.raises(FractionError):
        parse_mixed("1/-3")
    with pytest.raises(FractionError):
        parse_mixed("- 1/3")


def test_parse_mixed_empty_text_raises():
    with pytest.raises(FractionError):
        parse_mixed("")


def test_parse_mixed_fraction_error_is_a_value_error():
    with pytest.raises(ValueError):
        parse_mixed("half")


# --- format_repeating ---------------------------------------------------


def test_format_repeating_long_period():
    assert format_repeating(Fraction(1, 7)) == "0.(142857)"
    assert format_repeating(Fraction(1, 13)) == "0.(076923)"


def test_format_repeating_whole_number_has_no_point():
    assert format_repeating(3) == "3"
    assert format_repeating(Fraction(10, 5)) == "2"
    assert format_repeating(0) == "0"


def test_format_repeating_zero_inside_the_decimals():
    assert format_repeating(Fraction(1, 101)) == "0.(0099)"
    assert format_repeating(Fraction(91, 90)) == "1.0(1)"


def test_format_repeating_long_repeating_part_is_written_in_full():
    assert format_repeating(Fraction(1, 97)) == (
        "0.(010309278350515463917525773195876288659793814432989690721649484536082474226804123711340206185567)"
    )


def test_format_repeating_bool_raises_type_error():
    with pytest.raises(TypeError):
        format_repeating(True)


# --- parse_repeating ----------------------------------------------------


def test_parse_repeating_long_period():
    assert parse_repeating("3.(142857)") == Fraction(22, 7)


def test_parse_repeating_sign_applies_to_the_whole_number():
    assert parse_repeating("-0.5") == Fraction(-1, 2)
    assert parse_repeating("-0.(3)") == Fraction(-1, 3)
    assert parse_repeating("-3.(142857)") == Fraction(-22, 7)


def test_parse_repeating_forms_that_format_repeating_never_writes():
    assert parse_repeating("0.3(3)") == Fraction(1, 3)
    assert parse_repeating("0.(33)") == Fraction(1, 3)
    assert parse_repeating("2.(0)") == 2
    assert parse_repeating("1.50") == Fraction(3, 2)


def test_parse_repeating_round_trip_with_format_repeating():
    assert parse_repeating(format_repeating(Fraction(1, 44))) == Fraction(1, 44)
    assert parse_repeating(format_repeating(Fraction(-355, 113))) == Fraction(-355, 113)
    assert format_repeating(parse_repeating("0.1(6)")) == "0.1(6)"


def test_parse_repeating_empty_parentheses_raise():
    with pytest.raises(FractionError):
        parse_repeating("0.()")


def test_parse_repeating_parentheses_without_point_raise():
    with pytest.raises(FractionError):
        parse_repeating("1(3)")


def test_parse_repeating_inner_spaces_raise():
    with pytest.raises(FractionError):
        parse_repeating("0. (3)")
    with pytest.raises(FractionError):
        parse_repeating("- 0.5")
