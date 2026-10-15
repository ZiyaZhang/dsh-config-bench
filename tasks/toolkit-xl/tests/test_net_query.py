import pytest

from toolkit.net.query import (
    QueryError,
    build_query,
    decode_component,
    encode_component,
    parse_query,
    parse_query_dict,
    update_query,
)


# --- decode_component ---------------------------------------------------


def test_decode_component_plain_text_is_unchanged():
    assert decode_component("hello-world_1.0~") == "hello-world_1.0~"


def test_decode_component_plus_is_a_space_by_default():
    assert decode_component("two+words") == "two words"


def test_decode_component_escaped_plus_stays_a_plus():
    assert decode_component("1%2B1") == "1+1"


def test_decode_component_three_byte_utf8_sequence():
    assert decode_component("%E2%82%AC5") == "\u20ac5"


def test_decode_component_empty_text():
    assert decode_component("") == ""


def test_decode_component_one_hex_digit_before_text_raises_query_error():
    with pytest.raises(QueryError):
        decode_component("%4g")


def test_decode_component_signed_hex_raises_query_error():
    with pytest.raises(QueryError):
        decode_component("%+1")


def test_decode_component_invalid_utf8_raises_query_error():
    with pytest.raises(QueryError):
        decode_component("%FF")


# --- encode_component ---------------------------------------------------


def test_encode_component_unreserved_characters_are_unchanged():
    text = "AZaz09-._~"
    assert encode_component(text) == text


def test_encode_component_plus_is_escaped():
    assert encode_component("1+1") == "1%2B1"


def test_encode_component_uses_upper_case_hex():
    assert encode_component("\u00e9:") == "%C3%A9%3A"


def test_encode_component_newline_and_low_bytes_have_two_digits():
    assert encode_component("a\nb\tc") == "a%0Ab%09c"


# --- parse_query --------------------------------------------------------


def test_parse_query_result_is_a_list_of_tuples():
    result = parse_query("a=1")
    assert type(result) is list and type(result[0]) is tuple


def test_parse_query_only_one_question_mark_is_dropped():
    assert parse_query("??a=1") == [("?a", "1")]


def test_parse_query_empty_key_is_kept():
    assert parse_query("=1") == [("", "1")]


def test_parse_query_empty_text_gives_empty_list():
    assert parse_query("") == [] and parse_query("?") == [] and parse_query("&&") == []


def test_parse_query_escaped_separators_do_not_split():
    assert parse_query("a%26b=c%3Dd") == [("a&b", "c=d")]


def test_parse_query_malformed_escape_in_key_raises_query_error():
    with pytest.raises(QueryError):
        parse_query("ok=1&b%zz=2")


# --- parse_query_dict ---------------------------------------------------


def test_parse_query_dict_key_without_value_contributes_none():
    assert parse_query_dict("flag&flag=&flag=x") == {"flag": [None, "", "x"]}


# --- build_query --------------------------------------------------------


def test_build_query_from_pairs():
    assert build_query([("a", "1"), ("b", "2")]) == "a=1&b=2"


def test_build_query_empty_string_writes_an_equals_sign():
    assert build_query([("flag", "")]) == "flag="


def test_build_query_empty_list_writes_nothing():
    assert build_query({"a": "1", "gone": [], "b": "2"}) == "a=1&b=2"


def test_build_query_numbers_use_str():
    assert build_query({"n": 5, "x": 1.5, "zero": 0, "one": 1}) == "n=5&x=1.5&zero=0&one=1"


def test_build_query_has_no_leading_question_mark():
    assert build_query({"a": "1"})[0] == "a"


def test_build_query_sort_is_stable_for_equal_keys():
    assert build_query([("b", "9"), ("a", "2"), ("b", "0"), ("b", "5")], sort=True) == "a=2&b=9&b=0&b=5"


def test_build_query_sort_by_position_with_list_values():
    assert build_query({"z": ["2", "1"], "a": "x"}, True) == "a=x&z=2&z=1"


def test_build_query_does_not_modify_its_argument():
    pairs = [("b", ["2", "1"]), ("a", None)]
    build_query(pairs, sort=True)
    assert pairs == [("b", ["2", "1"]), ("a", None)]


# --- update_query -------------------------------------------------------


def test_update_query_repeated_key_keeps_the_first_position_only():
    assert update_query("a=1&b=2&a=3&c=4&a=5", {"a": "9"}) == "a=9&b=2&c=4"


def test_update_query_none_value_writes_the_key_alone():
    assert update_query("a=1&b=2", {"a": None}) == "a&b=2"


def test_update_query_rewrites_unchanged_pairs_in_canonical_encoding():
    assert update_query("x=%7e&y=a%20b&&z", {"n": 1}) == "x=~&y=a+b&z&n=1"


def test_update_query_malformed_text_raises_query_error():
    with pytest.raises(QueryError):
        update_query("a=%", {"b": "1"})


