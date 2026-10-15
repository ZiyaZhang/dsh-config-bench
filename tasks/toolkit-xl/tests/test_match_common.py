import pytest

from toolkit.match.common import (
    common_prefix,
    common_suffix,
    longest_common_subsequence,
    longest_common_substring,
)


# --- common_prefix ------------------------------------------------------


def test_common_prefix_of_three_words():
    assert common_prefix(["interview", "internet", "interval"]) == "inter"


def test_common_prefix_of_equal_strings():
    assert common_prefix(["same", "same", "same"]) == "same"


def test_common_prefix_is_case_sensitive():
    assert common_prefix(["Hello", "hello"]) == ""


def test_common_prefix_no_strings_raises_value_error():
    with pytest.raises(ValueError):
        common_prefix([])


def test_common_prefix_with_separator_given_by_position():
    assert common_prefix(["a.b.c", "a.b.d"], ".") == "a.b"


def test_common_prefix_with_separator_no_segment_in_common():
    assert common_prefix(["abc/x", "abd/x"], sep="/") == ""


def test_common_prefix_with_separator_keeps_empty_segments():
    assert common_prefix(["a//b/c", "a//b/d"], sep="/") == "a//b"


# --- common_suffix ------------------------------------------------------


def test_common_suffix_of_three_words():
    assert common_suffix(["walking", "talking", "king"]) == "king"


def test_common_suffix_when_one_string_is_a_suffix_of_the_other():
    assert common_suffix(["bar", "foobar"]) == "bar"


def test_common_suffix_no_strings_raises_value_error():
    with pytest.raises(ValueError):
        common_suffix([])


def test_common_suffix_with_separator_given_by_position():
    assert common_suffix(["a/src/main.py", "b/src/main.py"], "/") == "src/main.py"


# --- longest_common_substring -------------------------------------------


def test_longest_common_substring_in_the_middle():
    assert longest_common_substring("the quick fox", "a quick dog") == " quick "


def test_longest_common_substring_when_one_contains_the_other():
    assert longest_common_substring("xxhelloxx", "hello") == "hello"


def test_longest_common_substring_tie_takes_the_first_in_a():
    assert longest_common_substring("abcxyz", "xyzabc") == "abc"


def test_longest_common_substring_longer_match_beats_earlier_one():
    assert longest_common_substring("ab-abcd", "abcd ab") == "abcd"


def test_longest_common_substring_long_strings_of_one_character():
    assert longest_common_substring("a" * 250, "a" * 240) == "a" * 240


# --- longest_common_subsequence -----------------------------------------


def test_longest_common_subsequence_nothing_in_common_is_empty():
    assert longest_common_subsequence("abc", "xyz") == ""


def test_longest_common_subsequence_need_not_be_one_piece():
    assert longest_common_subsequence("abcde", "abXde") == "abde"


def test_longest_common_subsequence_tie_depends_on_first_argument():
    assert longest_common_subsequence("ba", "ab") == "b"


def test_longest_common_subsequence_earliest_index_list_not_smallest_string():
    assert longest_common_subsequence("zay", "yaz") == "z"


def test_longest_common_subsequence_repeated_characters():
    assert longest_common_subsequence("aaa", "aa") == "aa"


