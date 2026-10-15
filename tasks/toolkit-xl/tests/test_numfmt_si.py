from fractions import Fraction

import pytest

from toolkit.numfmt.si import SIError, format_bytes, format_si, parse_bytes, parse_si


# --- format_si ----------------------------------------------------------


def test_format_si_value_below_thousand_has_no_prefix():
    assert format_si(5) == "5.0"
    assert format_si(999) == "999.0"


def test_format_si_smaller_prefixes():
    assert format_si(0.002) == "2.0m"
    assert format_si(Fraction(3, 10 ** 6)) == "3.0u"
    assert format_si(Fraction(4, 10 ** 9)) == "4.0n"
    assert format_si(Fraction(5, 10 ** 12)) == "5.0p"


def test_format_si_decimals_parameter():
    assert format_si(1234, 0) == "1k"
    assert format_si(1234, 3) == "1.234k"
    assert format_si(1234, decimals=2) == "1.23k"


def test_format_si_switches_prefix_when_rounded_mantissa_reaches_thousand():
    assert format_si(999.94) == "999.9"
    assert format_si(Fraction(99995, 100)) == "1.0k"
    assert format_si(999.96) == "1.0k"


def test_format_si_switch_point_below_one():
    assert format_si(Fraction(99994, 100000)) == "999.9m"
    assert format_si(Fraction(99995, 100000)) == "1.0"


def test_format_si_value_below_the_smallest_prefix():
    assert format_si(Fraction(4, 10 ** 13)) == "0.4p"
    assert format_si(1e-15) == "0.0p"


def test_format_si_negative_value_written_as_zero_has_no_sign():
    assert format_si(-1e-15) == "0.0p"


def test_format_si_without_unit_has_no_space():
    assert format_si(47e-9, 0) == "47n"


def test_format_si_nan_and_infinity_raise_value_error():
    with pytest.raises(ValueError):
        format_si(float("nan"))
    with pytest.raises(ValueError):
        format_si(float("inf"))


# --- parse_si -----------------------------------------------------------


def test_parse_si_kilo():
    assert parse_si("1.5k") == 1500


def test_parse_si_result_is_exact():
    assert parse_si("0.1k") == 100
    assert parse_si("4.7m") == Fraction(47, 10000)


def test_parse_si_surrounding_whitespace_is_ignored():
    assert parse_si("  1.5k\n") == 1500


def test_parse_si_number_forms():
    assert parse_si(".5k") == 500
    assert parse_si("3.k") == 3000
    assert parse_si("007") == 7


def test_parse_si_without_unit_trailing_m_is_milli():
    assert parse_si("5m") == Fraction(5, 1000)


def test_parse_si_unknown_prefix_raises():
    with pytest.raises(SIError):
        parse_si("1.5x")
    with pytest.raises(SIError):
        parse_si("3da")


def test_parse_si_empty_text_raises():
    with pytest.raises(SIError):
        parse_si("")
    with pytest.raises(SIError):
        parse_si("   ")


def test_parse_si_missing_unit_raises():
    with pytest.raises(SIError):
        parse_si("1.5k", unit="Hz")


def test_parse_si_error_is_a_value_error():
    with pytest.raises(ValueError):
        parse_si("abc")


# --- format_bytes -------------------------------------------------------


def test_format_bytes_kibibytes():
    assert format_bytes(1024) == "1.0 KiB"
    assert format_bytes(1536) == "1.5 KiB"


def test_format_bytes_decimals_parameter():
    assert format_bytes(123456789, 2) == "117.74 MiB"
    assert format_bytes(123456789, decimals=0) == "118 MiB"


def test_format_bytes_switch_point_with_zero_decimals():
    assert format_bytes(1048063, 0) == "1023 KiB"
    assert format_bytes(1048064, 0) == "1 MiB"


def test_format_bytes_negative_count_raises_value_error():
    with pytest.raises(ValueError):
        format_bytes(-1)


# --- parse_bytes --------------------------------------------------------


def test_parse_bytes_plain_bytes():
    result = parse_bytes("512 B")
    assert type(result) is int and result == 512


def test_parse_bytes_fractional_number():
    assert parse_bytes("1.5 KiB") == 1536
    assert parse_bytes(".5 MB") == 500000


def test_parse_bytes_round_trip_with_format_bytes():
    assert parse_bytes(format_bytes(1536)) == 1536
    assert parse_bytes(format_bytes(5 * 1024 ** 3, 0)) == 5 * 1024 ** 3


def test_parse_bytes_missing_unit_raises():
    with pytest.raises(SIError):
        parse_bytes("1024")


def test_parse_bytes_unknown_unit_raises():
    with pytest.raises(SIError):
        parse_bytes("1 bytes")
    with pytest.raises(SIError):
        parse_bytes("1 EiB")


