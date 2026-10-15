from fractions import Fraction

import pytest

import toolkit.numfmt
from toolkit.numfmt.fraction import FractionError
from toolkit.numfmt.grouping import GroupingError
from toolkit.numfmt.ordinal import NumeralError
from toolkit.numfmt.si import SIError


# --- reformat_number ----------------------------------------------------


def test_reformat_number_grouped_to_words():
    result = toolkit.numfmt.reformat_number("1,234", "grouped", "words")
    assert result == "one thousand two hundred and thirty-four"


def test_reformat_number_mixed_to_repeating():
    assert toolkit.numfmt.reformat_number("2 1/3", "mixed", "repeating") == "2.(3)"


def test_reformat_number_grouped_to_si_uses_one_decimal():
    assert toolkit.numfmt.reformat_number("1,500", "grouped", "si") == "1.5k"


def test_reformat_number_roman_to_other_targets():
    assert toolkit.numfmt.reformat_number("XII", "roman", "grouped") == "12.00"
    assert toolkit.numfmt.reformat_number("XII", "roman", "words") == "twelve"
    assert toolkit.numfmt.reformat_number("MMXXIV", "roman", "si") == "2.0k"


def test_reformat_number_negative_value_to_words():
    assert toolkit.numfmt.reformat_number("-1,001", "grouped", "words") == "minus one thousand and one"


def test_reformat_number_roman_range_error_is_raised_unchanged():
    with pytest.raises(ValueError):
        toolkit.numfmt.reformat_number("4,000", "grouped", "roman")


def test_reformat_number_unknown_target_raises_value_error():
    with pytest.raises(ValueError):
        toolkit.numfmt.reformat_number("12", "grouped", "binary")


# --- re-exports ---------------------------------------------------------


def test_numfmt_facade_exposes_grouping_functions():
    assert toolkit.numfmt.round_exact(2.5) == Fraction(2)
    assert toolkit.numfmt.format_grouped(1234.5) == "1,234.50"
    assert toolkit.numfmt.parse_grouped("1,234.5") == Fraction(2469, 2)


def test_numfmt_facade_exposes_fraction_functions():
    assert toolkit.numfmt.format_mixed(Fraction(3, 2)) == "1 1/2"
    assert toolkit.numfmt.parse_mixed("1 1/2") == Fraction(3, 2)
    assert toolkit.numfmt.format_repeating(Fraction(1, 3)) == "0.(3)"
    assert toolkit.numfmt.parse_repeating("0.(3)") == Fraction(1, 3)


