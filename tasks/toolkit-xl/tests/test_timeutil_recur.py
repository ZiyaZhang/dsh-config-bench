import pytest

from toolkit.timeutil.recur import (
    RecurError,
    expand_rule,
    format_rule,
    next_occurrence,
    parse_rule,
)


# --- parse_rule: accepted texts -----------------------------------------


def test_parse_rule_daily_with_count():
    assert parse_rule("every day for 3 times") == {
        "unit": "day",
        "interval": 1,
        "weekdays": None,
        "count": 3,
        "until": None,
    }


def test_parse_rule_plural_with_interval_one():
    rule = parse_rule("every 1 days for 2 times")
    assert rule["unit"] == "day" and rule["interval"] == 1


def test_parse_rule_interval_with_several_digits():
    assert parse_rule("every 120 days for 2 times")["interval"] == 120


def test_parse_rule_weekdays_value_is_a_tuple():
    assert type(parse_rule("every week on fri for 2 times")["weekdays"]) is tuple


def test_parse_rule_until_last_day_of_each_month():
    lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    texts = [
        "every day until 2023-%02d-%02d" % (month, days) for month, days in enumerate(lengths, 1)
    ]
    dates = [parse_rule(text)["until"] for text in texts]
    assert dates == [(2023, month, days) for month, days in enumerate(lengths, 1)]


# --- parse_rule: errors -------------------------------------------------


def test_parse_rule_empty_text_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("")


def test_parse_rule_other_first_word_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("each day for 2 times")


def test_parse_rule_interval_with_leading_zero_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("every 02 days for 2 times")


def test_parse_rule_missing_unit_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("every 2 for 2 times")


def test_parse_rule_full_weekday_name_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("every week on monday for 2 times")


def test_parse_rule_space_in_weekday_list_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("every week on mon, wed for 2 times")


def test_parse_rule_until_day_after_the_end_of_each_month_raises_recur_error():
    for month, days in enumerate([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], 1):
        with pytest.raises(RecurError):
            parse_rule("every day until 2023-%02d-%02d" % (month, days + 1))


def test_parse_rule_until_a_missing_day_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("every week until 2023-02-29")


def test_parse_rule_until_year_zero_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("every week until 0000-01-05")


def test_parse_rule_other_word_after_count_raises_recur_error():
    with pytest.raises(RecurError):
        parse_rule("every day for 3 days")


def test_parse_rule_error_is_a_value_error():
    with pytest.raises(ValueError):
        parse_rule("daily")


# --- format_rule --------------------------------------------------------


def test_format_rule_weekday_names_in_ascending_order():
    rule = {"unit": "week", "interval": 1, "weekdays": (0, 1, 3), "count": 2, "until": None}
    assert format_rule(rule) == "every week on sun,mon,wed for 2 times"


def test_format_rule_does_not_modify_the_rule():
    rule = {"unit": "week", "interval": 2, "weekdays": (1, 3), "count": 4, "until": None}
    format_rule(rule)
    assert rule == {"unit": "week", "interval": 2, "weekdays": (1, 3), "count": 4, "until": None}


# --- expand_rule: days --------------------------------------------------


def test_expand_rule_every_day_with_count():
    assert expand_rule("every day for 3 times", (2024, 2, 28)) == [
        (2024, 2, 28),
        (2024, 2, 29),
        (2024, 3, 1),
    ]


def test_expand_rule_until_between_two_candidates():
    result = expand_rule("every 2 days until 2024-01-04", (2024, 1, 1))
    assert result == [(2024, 1, 1), (2024, 1, 3)]


def test_expand_rule_count_one_gives_start_only():
    assert expand_rule("every 5 days for 1 time", (2024, 6, 30)) == [(2024, 6, 30)]


def test_expand_rule_february_of_2000_has_29_days():
    result = expand_rule("every day for 3 times", (2000, 2, 28))
    assert result == [(2000, 2, 28), (2000, 2, 29), (2000, 3, 1)]


def test_expand_rule_in_year_9999():
    assert expand_rule("every day for 2 times", (9999, 1, 1)) == [(9999, 1, 1), (9999, 1, 2)]


# --- expand_rule: weeks -------------------------------------------------


def test_expand_rule_every_second_week():
    assert expand_rule("every 2 weeks for 3 times", (2024, 1, 3)) == [
        (2024, 1, 3),
        (2024, 1, 17),
        (2024, 1, 31),
    ]


def test_expand_rule_start_is_not_included_when_its_weekday_is_not_listed():
    result = expand_rule("every week on mon for 2 times", (2024, 1, 3))
    assert result == [(2024, 1, 8), (2024, 1, 15)]


def test_expand_rule_start_on_a_sunday_opens_its_week():
    assert expand_rule("every 2 weeks on sun,sat for 3 times", (2024, 1, 7)) == [
        (2024, 1, 7),
        (2024, 1, 13),
        (2024, 1, 21),
    ]


def test_expand_rule_weekdays_until_before_the_first_candidate():
    assert expand_rule("every week on mon until 2024-01-07", (2024, 1, 3)) == []


# --- expand_rule: months ------------------------------------------------


def test_expand_rule_weekdays_in_the_year_2003():
    result = expand_rule("every week on sun for 2 times", (2003, 6, 10))
    assert result == [(2003, 6, 15), (2003, 6, 22)]


def test_expand_rule_every_month_keeps_the_day():
    assert expand_rule("every month for 3 times", (2024, 1, 15)) == [
        (2024, 1, 15),
        (2024, 2, 15),
        (2024, 3, 15),
    ]


def test_expand_rule_day_30_is_cut_only_in_february():
    assert expand_rule("every month for 3 times", (2024, 1, 30)) == [
        (2024, 1, 30),
        (2024, 2, 29),
        (2024, 3, 30),
    ]


def test_expand_rule_month_end_in_february_2000():
    assert expand_rule("every month for 2 times", (2000, 1, 31)) == [(2000, 1, 31), (2000, 2, 29)]


def test_expand_rule_months_with_until():
    assert expand_rule("every 2 months until 2024-07-01", (2024, 1, 31)) == [
        (2024, 1, 31),
        (2024, 3, 31),
        (2024, 5, 31),
    ]


# --- expand_rule: errors ------------------------------------------------


def test_expand_rule_start_month_zero_raises_value_error():
    with pytest.raises(ValueError):
        expand_rule("every day for 2 times", (2024, 0, 1))


def test_expand_rule_start_in_year_10000_raises_value_error():
    with pytest.raises(ValueError):
        expand_rule("every day for 2 times", (10000, 1, 1))


# --- next_occurrence ----------------------------------------------------


def test_next_occurrence_between_two_occurrences():
    result = next_occurrence("every 10 days for 5 times", (2024, 1, 1), (2024, 1, 15))
    assert result == (2024, 1, 21)


def test_next_occurrence_beyond_until_gives_none():
    assert next_occurrence("every day until 2024-01-10", (2024, 1, 1), (2024, 1, 10)) is None


def test_next_occurrence_invalid_start_raises_value_error():
    with pytest.raises(ValueError):
        next_occurrence("every day for 2 times", (2024, 2, 30), (2024, 1, 1))


