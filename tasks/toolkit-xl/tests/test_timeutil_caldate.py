import pytest

from toolkit.timeutil.caldate import (
    add_days,
    add_months,
    day_of_week,
    days_between,
    days_in_month,
    from_ordinal,
    is_leap_year,
    is_valid_date,
    to_ordinal,
)


# --- is_leap_year -------------------------------------------------------


def test_is_leap_year_divisible_by_four():
    assert is_leap_year(2024) is True


def test_is_leap_year_divisible_by_400():
    assert is_leap_year(2000) is True


# --- days_in_month ------------------------------------------------------


def test_days_in_month_all_months_of_a_common_year():
    lengths = [days_in_month(2023, month) for month in range(1, 13)]
    assert lengths == [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def test_days_in_month_february_of_year_zero():
    assert days_in_month(0, 2) == 29


# --- is_valid_date ------------------------------------------------------


def test_is_valid_date_ordinary_date():
    assert is_valid_date((2024, 7, 4)) is True


def test_is_valid_date_29_february_of_a_common_year():
    assert is_valid_date((2023, 2, 29)) is False


def test_is_valid_date_month_out_of_range():
    assert is_valid_date((2023, 0, 1)) is False and is_valid_date((2023, 13, 1)) is False


def test_is_valid_date_four_elements():
    assert is_valid_date((2023, 4, 1, 0)) is False


def test_is_valid_date_string_elements():
    assert is_valid_date(("2023", "4", "1")) is False


# --- to_ordinal ---------------------------------------------------------


def test_to_ordinal_end_of_year_one():
    assert to_ordinal((1, 12, 31)) == 365 and to_ordinal((2, 1, 1)) == 366


def test_to_ordinal_unix_epoch():
    assert to_ordinal([1970, 1, 1]) == 719163


def test_to_ordinal_negative_year():
    assert to_ordinal((-1, 12, 31)) == -366 and to_ordinal((-1, 1, 1)) == -730


def test_to_ordinal_invalid_date_raises_value_error():
    with pytest.raises(ValueError):
        to_ordinal((2023, 2, 29))


# --- from_ordinal -------------------------------------------------------


def test_from_ordinal_leap_day():
    assert from_ordinal(738945) == (2024, 2, 29)


def test_from_ordinal_far_negative_number():
    assert from_ordinal(-146096) == (-399, 1, 1)


# --- day_of_week --------------------------------------------------------


def test_day_of_week_friday_is_five():
    assert day_of_week((2024, 3, 1)) == 5


def test_day_of_week_monday_is_one():
    assert day_of_week((2024, 1, 1)) == 1


def test_day_of_week_in_year_zero_and_before():
    assert day_of_week((0, 12, 31)) == 0 and day_of_week((-1, 12, 31)) == 5


# --- add_days -----------------------------------------------------------


def test_add_days_across_the_end_of_february_in_a_common_year():
    assert add_days((2023, 2, 28), 1) == (2023, 3, 1)


def test_add_days_many_days():
    assert add_days((2000, 1, 1), 10000) == (2027, 5, 19)


# --- add_months ---------------------------------------------------------


def test_add_months_keeps_the_day():
    assert add_months((2024, 1, 15), 1) == (2024, 2, 15)


def test_add_months_twelve_months_are_a_year():
    assert add_months((2024, 3, 15), -12) == (2023, 3, 15)


def test_add_months_last_day_of_january_gives_last_day_of_february():
    assert add_months((2023, 1, 31), 1) == (2023, 2, 28)


def test_add_months_leap_day_gives_last_day_of_march():
    assert add_months((2024, 2, 29), 1) == (2024, 3, 31)


def test_add_months_last_day_of_february_one_year_later():
    assert add_months((2023, 2, 28), 12) == (2024, 2, 29)


def test_add_months_back_before_year_one():
    assert add_months((1, 1, 15), -1) == (0, 12, 15) and add_months((1, 1, 15), -13) == (-1, 12, 15)


# --- days_between -------------------------------------------------------


def test_days_between_is_negative_when_the_second_date_is_earlier():
    assert days_between((2024, 3, 1), (2024, 2, 1)) == -29


def test_days_between_across_year_zero():
    assert days_between((0, 1, 1), (1, 1, 1)) == 366


