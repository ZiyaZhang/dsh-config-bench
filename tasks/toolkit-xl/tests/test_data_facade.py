import pytest

import toolkit.data
from toolkit.data.csvlite import CSVError
from toolkit.data.ini import INIError
from toolkit.data.jsonpath import JSONPathError


# --- query --------------------------------------------------------------


def test_query_csv_is_the_default_format():
    assert toolkit.data.query("name,age\nann,3\nbob,5\n", "$[*].name") == ["ann", "bob"]


def test_query_csv_negative_index_selects_last_record():
    assert toolkit.data.query("k\na\nb\nc\n", "$[-1].k", "csv") == ["c"]


def test_query_ini_wildcard_gives_typed_values_in_order():
    text = "[opts]\ndebug = yes\nlevel = 3\nname = demo\nnothing = null\n"
    result = toolkit.data.query(text, "$.opts.*", fmt="ini")
    assert result == [True, 3, "demo", None]
    assert [type(value) for value in result] == [bool, int, str, type(None)]


def test_query_without_match_gives_empty_list():
    assert toolkit.data.query("[a]\nx = 1\n", "$.b.x", "ini") == []


def test_query_malformed_csv_raises_csv_error():
    with pytest.raises(CSVError):
        toolkit.data.query('a,b\n"1,2\n', "$")


# --- re-exports ---------------------------------------------------------


def test_facade_exposes_ini_functions():
    assert toolkit.data.parse_ini("[s]\nk = 1\n") == {"s": {"k": 1}}
    assert toolkit.data.parse_value(" off ") is False


def test_data_facade_error_classes_are_the_classes_of_the_modules():
    with pytest.raises(CSVError):
        toolkit.data.parse_csv('"open')
    assert toolkit.data.CSVError is CSVError
    assert toolkit.data.INIError is INIError
    assert toolkit.data.JSONPathError is JSONPathError
