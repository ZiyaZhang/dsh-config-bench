import pytest

import toolkit.timeutil
from toolkit.timeutil.cron import CronError
from toolkit.timeutil.duration import DurationError
from toolkit.timeutil.recur import RecurError


# --- upcoming -----------------------------------------------------------


def test_upcoming_every_quarter_of_an_hour_within_one_hour():
    assert toolkit.timeutil.upcoming("*/15 * * * *", (2024, 1, 1, 0, 0), "1h") == [
        (2024, 1, 1, 0, 15),
        (2024, 1, 1, 0, 30),
        (2024, 1, 1, 0, 45),
        (2024, 1, 1, 1, 0),
    ]


def test_upcoming_seconds_that_do_not_fill_a_minute_are_dropped():
    assert toolkit.timeutil.upcoming("0 0 * * *", (2024, 2, 27, 12, 0), "2d 11h 59m 59s") == [
        (2024, 2, 28, 0, 0),
        (2024, 2, 29, 0, 0),
    ]


def test_upcoming_zero_duration_gives_empty_list():
    assert toolkit.timeutil.upcoming("* * * * *", (2024, 1, 1, 0, 0), "0s") == []


def test_upcoming_window_across_the_end_of_the_year():
    result = toolkit.timeutil.upcoming("0 0 1 * *", (2023, 12, 15, 0, 0), "30d")
    assert result == [(2024, 1, 1, 0, 0)]


def test_upcoming_result_is_a_list_of_tuples():
    result = toolkit.timeutil.upcoming("0 12 * * *", [2024, 1, 1, 0, 0], "1d")
    assert type(result) is list and type(result[0]) is tuple and result == [(2024, 1, 1, 12, 0)]


def test_upcoming_malformed_expression_raises_cron_error():
    with pytest.raises(CronError):
        toolkit.timeutil.upcoming("* * * *", (2024, 1, 1, 0, 0), "1h")


# --- re-exports ---------------------------------------------------------


def test_timeutil_facade_exposes_cron_functions():
    assert toolkit.timeutil.parse_cron("0 0 1 1 0") == ((0,), (0,), (1,), (1,), (0,))
    assert toolkit.timeutil.cron_matches("0 0 * * *", (0, 0, 5, 5, 5)) is True
    assert toolkit.timeutil.next_match("0 0 * * *", (2024, 1, 1, 0, 0)) == (2024, 1, 2, 0, 0)


def test_timeutil_facade_error_classes_are_the_classes_of_the_modules():
    with pytest.raises(DurationError):
        toolkit.timeutil.parse_duration("soon")
    assert toolkit.timeutil.DurationError is DurationError
    assert toolkit.timeutil.CronError is CronError
    assert toolkit.timeutil.RecurError is RecurError
