import pytest

from toolkit.timeutil.duration import (
    DurationError,
    format_duration,
    normalize_duration,
    parse_duration,
    round_duration,
)


# --- parse_duration: accepted texts -------------------------------------


def test_parse_duration_hours_and_minutes():
    assert parse_duration("1h30m") == 5400


def test_parse_duration_all_five_units():
    assert parse_duration("1w2d3h4m5s") == 788645


def test_parse_duration_any_whitespace_between_components():
    assert parse_duration("1h \t 5s") == 3605


def test_parse_duration_negative_zero_is_zero():
    assert parse_duration("-0h") == 0


def test_parse_duration_counts_are_not_limited():
    assert parse_duration("100h90m") == 365400


# --- parse_duration: fractions and rounding -----------------------------


def test_parse_duration_half_a_second_rounds_up():
    assert parse_duration("0.5s") == 1


def test_parse_duration_negative_half_rounds_away_from_zero():
    assert parse_duration("-2.5s") == -3


def test_parse_duration_fraction_of_a_week():
    assert parse_duration("0.001w") == 605


# --- parse_duration: errors ---------------------------------------------


def test_parse_duration_empty_text_raises_duration_error():
    with pytest.raises(DurationError):
        parse_duration("")


def test_parse_duration_unit_without_number_raises_duration_error():
    with pytest.raises(DurationError):
        parse_duration("h")


def test_parse_duration_upper_case_unit_raises_duration_error():
    with pytest.raises(DurationError):
        parse_duration("1H")


def test_parse_duration_number_starting_with_a_dot_raises_duration_error():
    with pytest.raises(DurationError):
        parse_duration(".5h")


def test_parse_duration_repeated_unit_raises_duration_error():
    with pytest.raises(DurationError):
        parse_duration("1h1h")


def test_parse_duration_fraction_of_zero_before_the_last_component_raises_duration_error():
    with pytest.raises(DurationError):
        parse_duration("1.0h30m")


def test_parse_duration_non_ascii_digit_raises_duration_error():
    with pytest.raises(DurationError):
        parse_duration("\u0661h")


def test_parse_duration_error_is_a_value_error():
    with pytest.raises(ValueError):
        parse_duration("soon")


# --- round_duration -----------------------------------------------------


def test_round_duration_negative_tie_goes_away_from_zero():
    assert round_duration(-90, "m") == -120


def test_round_duration_multiple_is_unchanged():
    assert round_duration(7200, "h") == 7200


def test_round_duration_to_hours():
    assert round_duration(5399, "h") == 3600 and round_duration(5400, "h") == 7200


def test_round_duration_result_is_an_int():
    result = round_duration(100, "m")
    assert type(result) is int and result == 120


def test_round_duration_unknown_unit_raises_value_error():
    with pytest.raises(ValueError):
        round_duration(90, "x")


# --- format_duration ----------------------------------------------------


def test_format_duration_zero_is_0s():
    assert format_duration(0) == "0s"


def test_format_duration_all_five_units():
    assert format_duration(694861) == "1w1d1h1m1s"


def test_format_duration_negative_gets_one_sign_in_front():
    assert format_duration(-90) == "-1m30s"


def test_format_duration_negative_with_separator():
    assert format_duration(-3605, separator=" ") == "-1h 5s"


def test_format_duration_max_parts_larger_than_needed():
    assert format_duration(86710, max_parts=9) == "1d5m10s"


def test_format_duration_max_parts_tie_rounds_up():
    assert format_duration(5370, max_parts=2) == "1h30m"


def test_format_duration_max_parts_one_rounds_to_the_leading_unit():
    assert format_duration(89, max_parts=1) == "1m" and format_duration(90, max_parts=1) == "2m"


def test_format_duration_max_parts_of_zero_seconds():
    assert format_duration(0, max_parts=1) == "0s"


def test_format_duration_invalid_separator_raises_value_error():
    with pytest.raises(ValueError):
        format_duration(90, "-")


# --- normalize_duration -------------------------------------------------


def test_normalize_duration_carries_seconds():
    assert normalize_duration("90s") == "1m30s"


def test_normalize_duration_seven_days_are_a_week():
    assert normalize_duration("7d") == "1w"


def test_normalize_duration_value_that_rounds_to_zero():
    assert normalize_duration("-0.2s") == "0s"


def test_normalize_duration_invalid_separator_raises_value_error():
    with pytest.raises(ValueError):
        normalize_duration("90s", ",")
