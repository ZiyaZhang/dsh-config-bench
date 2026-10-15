import pytest

from toolkit.calc.units import (
    UnitError,
    convert,
    convert_text,
    format_number,
    format_quantity,
    parse_quantity,
    unit_family,
)


# --- parse_quantity -----------------------------------------------------


def test_parse_quantity_number_and_unit():
    assert parse_quantity("3.5 km") == (3.5, "km")


def test_parse_quantity_value_is_float():
    value, unit = parse_quantity("7 m")
    assert type(value) is float and value == 7.0 and unit == "m"


def test_parse_quantity_leading_dot():
    assert parse_quantity(".5 mi") == (0.5, "mi")


def test_parse_quantity_unknown_unit_raises_unit_error():
    with pytest.raises(UnitError):
        parse_quantity("5 parsec")


def test_parse_quantity_empty_text_raises_unit_error():
    with pytest.raises(UnitError):
        parse_quantity("")


def test_parse_quantity_text_after_unit_raises_unit_error():
    with pytest.raises(UnitError):
        parse_quantity("5 km east")


# --- unit_family --------------------------------------------------------


def test_unit_family_of_length_units():
    units = ["mm", "cm", "m", "km", "in", "ft", "yd", "mi"]
    assert [unit_family(unit) for unit in units] == ["length"] * 8


def test_unit_family_unknown_unit_raises_unit_error():
    with pytest.raises(UnitError):
        unit_family("mile")


# --- convert ------------------------------------------------------------


def test_convert_inches_to_centimetres():
    assert convert(10, "in", "cm") == pytest.approx(25.4, rel=1e-9, abs=1e-9)


def test_convert_centimetres_to_metres():
    assert convert(250, "cm", "m") == pytest.approx(2.5, rel=1e-9, abs=1e-9)


def test_convert_ounces_to_pounds():
    assert convert(16, "oz", "lb") == pytest.approx(1.0, rel=1e-9, abs=1e-9)


def test_convert_grams_to_milligrams():
    assert convert(1.5, "g", "mg") == pytest.approx(1500.0, rel=1e-9, abs=1e-9)


def test_convert_weeks_to_days():
    assert convert(2, "wk", "d") == pytest.approx(14.0, rel=1e-9, abs=1e-9)


def test_convert_same_unit_gives_same_value():
    assert convert(12.5, "kg", "kg") == pytest.approx(12.5, rel=1e-9, abs=1e-9)


def test_convert_between_families_raises_unit_error():
    with pytest.raises(UnitError):
        convert(1, "kg", "m")


# --- format_number ------------------------------------------------------


def test_format_number_strips_trailing_zeros():
    assert format_number(2.5) == "2.5"


def test_format_number_precision_two():
    assert format_number(3.14159, 2) == "3.14"


def test_format_number_keeps_zeros_of_whole_number_with_precision_zero():
    assert format_number(1200, 0) == "1200"


def test_format_number_tiny_negative_value_is_zero_without_sign():
    assert format_number(-0.0004) == "0"


def test_format_number_rounding_can_reach_next_whole_number():
    assert format_number(1.9996) == "2"


# --- format_quantity ----------------------------------------------------


def test_format_quantity_joins_number_and_unit_with_space():
    assert format_quantity(2.5, "km") == "2.5 km"


def test_format_quantity_whole_value():
    assert format_quantity(12.0, "ft", precision=1) == "12 ft"


# --- convert_text -------------------------------------------------------


def test_convert_text_minutes_to_hours():
    assert convert_text("90 min", "h") == "1.5 h"


def test_convert_text_feet_to_inches_shows_no_float_noise():
    assert convert_text("1 ft", "in") == "12 in"


def test_convert_text_unknown_target_unit_raises_unit_error():
    with pytest.raises(UnitError):
        convert_text("3 km", "leagues")
