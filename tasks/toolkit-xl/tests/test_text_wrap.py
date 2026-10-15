import pytest

from toolkit.text.wrap import fill, shorten, wrap_lines


# --- wrap_lines ---------------------------------------------------------


def test_wrap_lines_empty_text_gives_empty_list():
    assert wrap_lines("") == []


def test_wrap_lines_default_width_is_70():
    text = "a" * 35 + " " + "b" * 34 + " " + "c" * 36 + " " + "d" * 34
    assert wrap_lines(text) == ["a" * 35 + " " + "b" * 34, "c" * 36, "d" * 34]


def test_wrap_lines_collapses_all_kinds_of_whitespace():
    assert wrap_lines("  one\t two\n\nthree  ", 20) == ["one two three"]


def test_wrap_lines_indent_counts_towards_width():
    assert wrap_lines("abc def", 8, initial_indent="    ") == ["    abc", "def"]


def test_wrap_lines_rest_of_split_word_shares_line_with_next_words():
    assert wrap_lines("abcdefg hi j", 5) == ["abcde", "fg hi", "j"]


def test_wrap_lines_width_one_gives_one_character_per_line():
    assert wrap_lines("ab c", 1) == ["a", "b", "c"]


def test_wrap_lines_validates_width_even_for_empty_text():
    with pytest.raises(ValueError):
        wrap_lines("", 0)


def test_wrap_lines_counts_code_points():
    text = "\u00e4\u00f6\u00fc \u00f1\u00e7 \u00e9\u00e8"
    assert wrap_lines(text, 6) == ["\u00e4\u00f6\u00fc \u00f1\u00e7", "\u00e9\u00e8"]


# --- fill ---------------------------------------------------------------


def test_fill_joins_lines_inside_a_paragraph():
    assert fill("one\ntwo\nthree", 20) == "one two three"


def test_fill_empty_text_gives_empty_string():
    assert fill("") == ""


def test_fill_wraps_each_paragraph_separately():
    assert fill("aa bb cc\n\ndd", 5) == "aa bb\ncc\n\ndd"


def test_fill_invalid_width_raises_value_error():
    with pytest.raises(ValueError):
        fill("text", 0)


# --- shorten ------------------------------------------------------------


def test_shorten_result_may_be_exactly_width():
    assert shorten("alpha beta gamma delta", 13) == "alpha beta..."


def test_shorten_width_equal_to_placeholder_length_is_allowed():
    assert shorten("extraordinary claims", 3) == "..."


def test_shorten_placeholder_alone_is_used_verbatim():
    assert shorten("extraordinary claims", 8, placeholder=" [..]") == " [..]"


def test_shorten_width_check_does_not_depend_on_text():
    with pytest.raises(ValueError):
        shorten("ab", 2)
