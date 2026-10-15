import pytest

from toolkit.data.diff import diff_lines, diff_stats, format_diff


# --- diff_lines ---------------------------------------------------------


def test_diff_lines_identical_texts_are_all_unchanged():
    assert diff_lines("a\nb\nc", "a\nb\nc") == [(" ", "a"), (" ", "b"), (" ", "c")]


def test_diff_lines_everything_removed_when_new_text_is_empty():
    assert diff_lines("a\nb", "") == [("-", "a"), ("-", "b")]


def test_diff_lines_line_removed_in_the_middle():
    assert diff_lines("a\nb\nc", "a\nc") == [(" ", "a"), ("-", "b"), (" ", "c")]


def test_diff_lines_swapped_lines_remove_first_on_a_tie():
    assert diff_lines("x\ny", "y\nx") == [("-", "x"), (" ", "y"), ("+", "x")]


def test_diff_lines_repeated_lines():
    expected = [(" ", "a"), ("-", "a"), (" ", "b"), ("+", "b")]
    assert diff_lines("a\na\nb", "a\nb\nb") == expected


def test_diff_lines_final_line_end_makes_no_difference():
    assert diff_lines("a\nb\n", "a\nb") == [(" ", "a"), (" ", "b")]


def test_diff_lines_empty_lines_are_lines():
    assert diff_lines("a\n\nb", "a\nb") == [(" ", "a"), ("-", ""), (" ", "b")]


# --- format_diff --------------------------------------------------------


def test_format_diff_identical_texts_without_context_shows_all_lines():
    assert format_diff("a\nb", "a\nb") == "  a\n  b"


def test_format_diff_context_one_shows_neighbouring_lines():
    old = "l1\nl2\nl3\nl4\nl5"
    new = "l1\nl2\nXX\nl4\nl5"
    assert format_diff(old, new, context=1) == "...\n  l2\n- l3\n+ XX\n  l4\n..."


def test_format_diff_one_marker_between_separate_changes():
    old = "a\nb\nc\nd\ne\nf\ng"
    new = "A\nb\nc\nd\ne\nf\nG"
    expected = "- a\n+ A\n  b\n...\n  f\n- g\n+ G"
    assert format_diff(old, new, context=1) == expected


def test_format_diff_context_by_position():
    assert format_diff("a\nb\nc", "a\nb\nC", 0) == "...\n- c\n+ C"


# --- diff_stats ---------------------------------------------------------


def test_diff_stats_of_two_empty_texts_is_all_zero():
    assert diff_stats("", "") == {"added": 0, "removed": 0, "unchanged": 0}


def test_diff_stats_uses_longest_common_subsequence():
    expected = {"added": 2, "removed": 2, "unchanged": 3}
    assert diff_stats("a\nb\nc\nd\ne", "c\nd\ne\na\nb") == expected
