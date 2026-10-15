import pytest

from toolkit.match.wildcard import GlobError, glob_escape, glob_filter, glob_match


# --- glob_match: literals, ? and * --------------------------------------


def test_glob_match_literal_pattern_matches_equal_path():
    assert glob_match("src/main.py", "src/main.py") is True


def test_glob_match_empty_pattern_matches_only_empty_path():
    assert glob_match("", "") is True
    assert glob_match("", "a") is False


def test_glob_match_star_matches_run_of_characters():
    assert glob_match("*.py", "setup.py") is True
    assert glob_match("a*c", "abbbc") is True


def test_glob_match_star_does_not_cross_separator():
    assert glob_match("*.py", "src/setup.py") is False
    assert glob_match("a*c", "a/c") is False


def test_glob_match_star_in_each_segment():
    assert glob_match("*/*", "a/b") is True
    assert glob_match("*/*", "a/b/c") is False
    assert glob_match("*/*", "ab") is False


# --- glob_match: ** -----------------------------------------------------


def test_glob_match_double_star_prefix_matches_any_depth():
    assert glob_match("**/*.py", "a/b/c.py") is True
    assert glob_match("**/*.py", "a/c.py") is True


def test_glob_match_double_star_prefix_matches_leading_separator():
    assert glob_match("**/x", "/x") is True


def test_glob_match_double_star_in_the_middle_keeps_the_separators():
    assert glob_match("a/**/b", "ab") is False
    assert glob_match("a/**/b", "a/xb") is False
    assert glob_match("a/**/b", "ax/b") is False


def test_glob_match_double_star_suffix_does_not_match_the_directory_itself():
    assert glob_match("src/**", "src") is False
    assert glob_match("src/**", "srcx/a") is False


def test_glob_match_double_star_before_text_after_separator_is_a_single_star():
    assert glob_match("a/**b", "a/xb") is True
    assert glob_match("a/**b", "a/x/b") is False


def test_glob_match_double_star_slash_at_the_end_needs_trailing_separator():
    assert glob_match("a/**/", "a/b/") is True
    assert glob_match("a/**/", "a/") is True
    assert glob_match("a/**/", "a/b") is False


# --- glob_match: classes ------------------------------------------------


def test_glob_match_class_lists_characters():
    assert glob_match("[abc]", "b") is True
    assert glob_match("[abc]", "d") is False


def test_glob_match_class_range_includes_both_ends():
    assert glob_match("[b-d]", "b") is True
    assert glob_match("[b-d]", "d") is True
    assert glob_match("[b-d]", "a") is False
    assert glob_match("[b-d]", "e") is False


def test_glob_match_class_negated_with_exclamation_mark():
    assert glob_match("[!abc]", "d") is True
    assert glob_match("[!abc]", "a") is False


def test_glob_match_class_never_matches_separator():
    assert glob_match("[!a]", "/") is False
    assert glob_match("a[/]b", "a/b") is False
    assert glob_match("[.-0]", "/") is False


def test_glob_match_hyphen_at_start_or_end_of_class_is_a_member():
    assert glob_match("[-a]", "-") is True
    assert glob_match("[a-]", "-") is True
    assert glob_match("[a-]", "b") is False


def test_glob_match_escaped_character_can_end_a_range():
    assert glob_match("[+-\\-]", ",") is True
    assert glob_match("[+-\\-]", ".") is False


def test_glob_match_class_compares_code_points():
    assert glob_match("[a-z]", "\u00e9") is False
    assert glob_match("[\u00e0-\u00ff]", "\u00e9") is True
    assert glob_match("[A-Z]", "b") is False


def test_glob_match_empty_class_is_unclosed():
    with pytest.raises(GlobError):
        glob_match("[]", "]")


def test_glob_match_class_ending_in_backslash_raises_glob_error():
    with pytest.raises(GlobError):
        glob_match("[a\\", "a")


# --- glob_match: escapes ------------------------------------------------


def test_glob_match_escaped_question_mark_and_bracket_are_literal():
    assert glob_match("a\\?", "a?") is True
    assert glob_match("a\\?", "ab") is False
    assert glob_match("\\[a]", "[a]") is True


def test_glob_match_escaped_separator_matches_a_separator():
    assert glob_match("a\\/b", "a/b") is True
    assert glob_match("a\\/b", "a\\/b") is False


def test_glob_match_escaped_star_next_to_star_is_no_double_star():
    assert glob_match("\\**", "*abc") is True
    assert glob_match("\\**", "*a/b") is False


# --- glob_filter --------------------------------------------------------


def test_glob_filter_keeps_matching_paths_in_order():
    paths = ["b.py", "a.txt", "a.py", "dir/c.py"]
    assert glob_filter("*.py", paths) == ["b.py", "a.py"]


def test_glob_filter_accepts_generator():
    assert glob_filter("?", (name for name in ["a", "bb", "c"])) == ["a", "c"]


def test_glob_filter_does_not_modify_the_paths():
    paths = ["b", "a"]
    glob_filter("a", paths)
    assert paths == ["b", "a"]


# --- glob_escape --------------------------------------------------------


def test_glob_escape_doubles_backslash():
    assert glob_escape("a\\b") == "a\\\\b"


def test_glob_escape_result_matches_the_text_itself():
    text = "what?[1]*\\x/**"
    assert glob_match(glob_escape(text), text) is True


