import pytest

from toolkit.numfmt.ordinal import (
    NumeralError,
    from_roman,
    ordinal_suffix,
    parse_ordinal,
    spell_number,
    to_ordinal,
    to_roman,
)


# --- ordinal_suffix and to_ordinal --------------------------------------


def test_ordinal_suffix_of_one_two_three():
    assert [ordinal_suffix(n) for n in (1, 2, 3)] == ["st", "nd", "rd"]


def test_ordinal_suffix_of_twenty_one_to_twenty_three():
    assert [ordinal_suffix(n) for n in (21, 22, 23)] == ["st", "nd", "rd"]


def test_ordinal_suffix_float_raises_type_error():
    with pytest.raises(TypeError):
        ordinal_suffix(1.0)


def test_to_ordinal_zero():
    assert to_ordinal(0) == "0th"


def test_to_ordinal_negative_number():
    assert to_ordinal(-1) == "-1st"
    assert to_ordinal(-12) == "-12th"


# --- parse_ordinal ------------------------------------------------------


def test_parse_ordinal_reads_the_number():
    assert parse_ordinal("21st") == 21
    assert parse_ordinal("112th") == 112


def test_parse_ordinal_wrong_suffix_raises():
    with pytest.raises(NumeralError):
        parse_ordinal("2th")
    with pytest.raises(NumeralError):
        parse_ordinal("11st")
    with pytest.raises(NumeralError):
        parse_ordinal("23nd")


def test_parse_ordinal_minus_zero_and_plus_sign_raise():
    with pytest.raises(NumeralError):
        parse_ordinal("-0th")
    with pytest.raises(NumeralError):
        parse_ordinal("+1st")


def test_parse_ordinal_error_is_a_value_error():
    with pytest.raises(ValueError):
        parse_ordinal("first")


# --- to_roman -----------------------------------------------------------


def test_to_roman_subtractive_forms():
    assert [to_roman(n) for n in (4, 9, 40, 90, 400, 900)] == ["IV", "IX", "XL", "XC", "CD", "CM"]


def test_to_roman_largest_number():
    assert to_roman(3999) == "MMMCMXCIX"


def test_to_roman_four_thousand_raises_value_error():
    with pytest.raises(ValueError):
        to_roman(4000)


# --- from_roman ---------------------------------------------------------


def test_from_roman_years():
    assert from_roman("MCMXCIV") == 1994
    assert from_roman("MMXXIV") == 2024


def test_from_roman_result_is_an_int():
    assert type(from_roman("XLII")) is int and from_roman("XLII") == 42


def test_from_roman_four_thousand_raises():
    with pytest.raises(NumeralError):
        from_roman("MMMM")


def test_from_roman_double_subtraction_raises():
    with pytest.raises(NumeralError):
        from_roman("IIV")
    with pytest.raises(NumeralError):
        from_roman("XXC")


def test_from_roman_wrong_order_raises():
    with pytest.raises(NumeralError):
        from_roman("IM")
    with pytest.raises(NumeralError):
        from_roman("VIX")


def test_from_roman_spaces_and_other_characters_raise():
    with pytest.raises(NumeralError):
        from_roman(" IV")
    with pytest.raises(NumeralError):
        from_roman("IV ")
    with pytest.raises(NumeralError):
        from_roman("ABC")
    with pytest.raises(NumeralError):
        from_roman("4")


# --- spell_number -------------------------------------------------------


def test_spell_number_tens():
    assert [spell_number(n) for n in range(20, 100, 10)] == [
        "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
    ]


def test_spell_number_hundreds_use_and_before_the_rest():
    assert spell_number(101) == "one hundred and one"
    assert spell_number(110) == "one hundred and ten"
    assert spell_number(342) == "three hundred and forty-two"
    assert spell_number(999) == "nine hundred and ninety-nine"


def test_spell_number_thousands_with_hundreds_get_no_extra_and():
    assert spell_number(1100) == "one thousand one hundred"
    assert spell_number(1234) == "one thousand two hundred and thirty-four"
    assert spell_number(2500) == "two thousand five hundred"


def test_spell_number_millions():
    assert spell_number(1000000) == "one million"
    assert spell_number(1000001) == "one million and one"
    assert spell_number(2000015) == "two million and fifteen"
    assert spell_number(1000100) == "one million one hundred"


def test_spell_number_largest_number():
    assert spell_number(999999999) == (
        "nine hundred and ninety-nine million nine hundred and ninety-nine thousand "
        "nine hundred and ninety-nine"
    )


def test_spell_number_too_small_raises_value_error():
    with pytest.raises(ValueError):
        spell_number(-1000000000)


