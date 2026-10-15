import pytest

from toolkit.data.jsonpath import JSONPathError, find_all, find_first, parse_path


# --- find_all: children and indexes -------------------------------------


def test_find_all_root_returns_whole_document():
    assert find_all({"a": 1}, "$") == [{"a": 1}]


def test_find_all_missing_key_gives_empty_list():
    assert find_all({"a": 1}, "$.b") == []


def test_find_all_negative_index_counts_from_end():
    assert find_all([10, 20, 30], "$[-1]") == [30]


def test_find_all_negative_index_out_of_range_gives_empty_list():
    assert find_all([10, 20, 30], "$[-4]") == []


def test_find_all_index_on_tuple_gives_empty_list():
    assert find_all({"t": (1, 2)}, "$.t[0]") == []


# --- find_all: wildcards ------------------------------------------------


def test_find_all_wildcard_on_list():
    assert find_all([1, [2], "x"], "$[*]") == [1, [2], "x"]


def test_find_all_wildcard_on_number_gives_empty_list():
    assert find_all({"a": 5}, "$.a[*]") == []


def test_find_all_wildcard_skips_items_without_the_key():
    data = [{"id": 1}, {"other": 2}, 7, {"id": 3}]
    assert find_all(data, "$[*].id") == [1, 3]


# --- find_all: quoted names ---------------------------------------------


def test_find_all_single_quoted_name_with_space():
    assert find_all({"first name": "ann"}, "$['first name']") == ["ann"]


def test_find_all_empty_quoted_name():
    assert find_all({"": "empty key"}, "$['']") == ["empty key"]


# --- find_all: malformed paths ------------------------------------------


def test_find_all_empty_path_raises_jsonpath_error():
    with pytest.raises(JSONPathError):
        find_all({"a": 1}, "")


def test_find_all_unclosed_bracket_raises_jsonpath_error():
    with pytest.raises(JSONPathError):
        find_all([1, 2], "$[0")


def test_find_all_index_with_plus_sign_raises_jsonpath_error():
    with pytest.raises(JSONPathError):
        find_all([1, 2], "$[+1]")


def test_find_all_text_after_quoted_name_raises_jsonpath_error():
    with pytest.raises(JSONPathError):
        find_all({"a": 1}, "$['a'x]")


def test_find_all_malformed_path_raises_even_if_nothing_could_match():
    with pytest.raises(JSONPathError):
        find_all(5, "$.a[")


# --- find_first ---------------------------------------------------------


def test_find_first_returns_none_by_default_when_nothing_matches():
    assert find_first({"a": 1}, "$.b") is None


def test_find_first_malformed_path_raises_jsonpath_error():
    with pytest.raises(JSONPathError):
        find_first({"a": 1}, "$a")


# --- parse_path ---------------------------------------------------------


def test_parse_path_index_steps_are_ints():
    assert parse_path("$[0][-12]") == [("index", 0), ("index", -12)]


def test_parse_path_mixed_steps():
    expected = [("key", "items"), ("index", 2), ("key", "tags"), ("wildcard", None), ("key", "a-b")]
    assert parse_path("$.items[2].tags[*]['a-b']") == expected


