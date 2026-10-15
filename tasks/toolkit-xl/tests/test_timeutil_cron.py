import pytest

from toolkit.timeutil.cron import CronError, cron_matches, next_match, parse_cron


# --- parse_cron: fields and items ---------------------------------------


def test_parse_cron_stars_allow_every_value():
    assert parse_cron("* * * * *") == (
        tuple(range(60)),
        tuple(range(24)),
        tuple(range(1, 32)),
        tuple(range(1, 13)),
        (0, 1, 2, 3, 4, 5, 6),
    )


def test_parse_cron_list_is_sorted():
    assert parse_cron("30,10,20 * * * *")[0] == (10, 20, 30)


def test_parse_cron_range_of_one_value():
    assert parse_cron("* * 3-3 * *")[2] == (3,)


def test_parse_cron_star_step_in_months_starts_at_one():
    assert parse_cron("* * * */5 *")[3] == (1, 6, 11)


def test_parse_cron_range_with_step():
    assert parse_cron("* 9-17/4 * * *")[1] == (9, 13, 17)


def test_parse_cron_step_of_one_changes_nothing():
    assert parse_cron("* * * * */1")[4] == (0, 1, 2, 3, 4, 5, 6)


def test_parse_cron_fields_may_be_separated_by_any_whitespace():
    assert parse_cron("  0\t12   1 1 *  ") == ((0,), (12,), (1,), (1,), (0, 1, 2, 3, 4, 5, 6))


# --- parse_cron: names and Sunday as 7 ----------------------------------


def test_parse_cron_weekday_names_in_a_range():
    assert parse_cron("* * * * mon-fri")[4] == (1, 2, 3, 4, 5)


def test_parse_cron_name_and_number_in_one_range():
    assert parse_cron("* * * 2-apr *")[3] == (2, 3, 4)


def test_parse_cron_zero_to_seven_is_every_weekday():
    assert parse_cron("* * * * 0-7")[4] == (0, 1, 2, 3, 4, 5, 6)


# --- parse_cron: errors -------------------------------------------------


def test_parse_cron_four_fields_raise_cron_error():
    with pytest.raises(CronError):
        parse_cron("* * * *")


def test_parse_cron_minute_60_raises_cron_error():
    with pytest.raises(CronError):
        parse_cron("60 * * * *")


def test_parse_cron_day_32_raises_cron_error():
    with pytest.raises(CronError):
        parse_cron("* * 1-32 * *")


def test_parse_cron_weekday_8_raises_cron_error():
    with pytest.raises(CronError):
        parse_cron("* * * * 8")


def test_parse_cron_saturday_to_sunday_runs_backwards():
    with pytest.raises(CronError):
        parse_cron("* * * * sat-sun")


def test_parse_cron_name_as_step_raises_cron_error():
    with pytest.raises(CronError):
        parse_cron("* * * */feb *")


def test_parse_cron_trailing_comma_raises_cron_error():
    with pytest.raises(CronError):
        parse_cron("1, * * * *")


def test_parse_cron_month_name_in_weekday_field_raises_cron_error():
    with pytest.raises(CronError):
        parse_cron("* * * * jan")


def test_parse_cron_question_mark_raises_cron_error():
    with pytest.raises(CronError):
        parse_cron("0 0 ? * 1")


def test_parse_cron_error_is_a_value_error():
    with pytest.raises(ValueError):
        parse_cron("every minute")


# --- cron_matches -------------------------------------------------------


def test_cron_matches_wrong_minute():
    assert cron_matches("30 8 * * *", (31, 8, 14, 2, 3)) is False


def test_cron_matches_weekday_restricted_only():
    assert cron_matches("0 9 * * mon-fri", (0, 9, 25, 12, 3)) is True
    assert cron_matches("0 9 * * mon-fri", (0, 9, 25, 12, 0)) is False


def test_cron_matches_both_restricted_weekday_alone_is_enough():
    assert cron_matches("0 0 13 * 5", (0, 0, 7, 6, 5)) is True


def test_cron_matches_full_weekday_range_is_not_a_restriction():
    assert cron_matches("0 0 13 * 0-6", (0, 0, 7, 6, 5)) is False


def test_cron_matches_star_with_step_one_is_not_a_restriction():
    assert cron_matches("0 0 */1 * 5", (0, 0, 13, 6, 2)) is False


def test_cron_matches_seven_in_expression_matches_sunday():
    assert cron_matches("* * * * 7", (0, 0, 1, 1, 0)) is True


def test_cron_matches_hour_out_of_range_raises_value_error():
    with pytest.raises(ValueError):
        cron_matches("* * * * *", (0, 24, 1, 1, 0))


def test_cron_matches_weekday_seven_in_moment_raises_value_error():
    with pytest.raises(ValueError):
        cron_matches("* * * * *", (0, 0, 1, 1, 7))


# --- next_match ---------------------------------------------------------


def test_next_match_never_returns_the_start():
    assert next_match("0 0 * * *", (2024, 1, 1, 0, 0)) == (2024, 1, 2, 0, 0)


def test_next_match_earlier_time_moves_to_the_next_day():
    assert next_match("15 8 * * *", (2024, 5, 10, 9, 0)) == (2024, 5, 11, 8, 15)


def test_next_match_february_has_29_days_in_2024():
    assert next_match("* * * * *", (2024, 2, 28, 23, 59)) == (2024, 2, 29, 0, 0)


def test_next_match_2000_is_a_leap_year():
    assert next_match("* * * * *", (2000, 2, 28, 23, 59)) == (2000, 2, 29, 0, 0)


def test_next_match_weekday_field():
    assert next_match("0 9 * * mon", (2024, 2, 28, 12, 0)) == (2024, 3, 4, 9, 0)


def test_next_match_weekday_of_the_start_date_in_a_leap_year():
    days = [next_match("0 0 * * mon", (2024, month, 1, 0, 0))[2] for month in range(1, 13)]
    assert days == [8, 5, 4, 8, 6, 3, 8, 5, 2, 7, 4, 2]


def test_next_match_weekday_in_the_year_1900():
    assert next_match("0 0 * * sun", (1900, 3, 1, 0, 0)) == (1900, 3, 4, 0, 0)


def test_next_match_day_or_weekday_takes_the_friday():
    assert next_match("0 0 13 * fri", (2024, 9, 1, 0, 0)) == (2024, 9, 6, 0, 0)


def test_next_match_day_31_skips_shorter_months():
    assert next_match("0 0 31 * *", (2024, 1, 31, 0, 0)) == (2024, 3, 31, 0, 0)


def test_next_match_limit_zero_gives_none():
    assert next_match("* * * * *", (2024, 5, 1, 12, 0), 0) is None


def test_next_match_date_that_never_exists_gives_none():
    assert next_match("0 0 31 2 *", (2024, 1, 31, 0, 0), limit=50000) is None


def test_next_match_start_on_a_missing_day_raises_value_error():
    with pytest.raises(ValueError):
        next_match("* * * * *", (2023, 2, 29, 0, 0))


def test_next_match_start_day_zero_raises_value_error():
    with pytest.raises(ValueError):
        next_match("* * * * *", (2024, 1, 0, 0, 0))


def test_next_match_start_hour_24_raises_value_error():
    with pytest.raises(ValueError):
        next_match("* * * * *", (2024, 1, 1, 24, 0))


def test_next_match_start_year_10000_raises_value_error():
    with pytest.raises(ValueError):
        next_match("* * * * *", (10000, 1, 1, 0, 0))


