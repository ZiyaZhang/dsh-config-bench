import pytest

import toolkit.match
from toolkit.match.editdist import ScriptError
from toolkit.match.wildcard import GlobError


# --- sorted_matches -----------------------------------------------------


def test_sorted_matches_selects_and_sorts_naturally():
    paths = ["b10.txt", "b2.txt", "notes.md", "b1.txt"]
    assert toolkit.match.sorted_matches("*.txt", paths) == ["b1.txt", "b2.txt", "b10.txt"]


def test_sorted_matches_ignore_case_does_not_change_the_matching():
    paths = ["a2.TXT", "a1.txt", "A3.txt"]
    assert toolkit.match.sorted_matches("a*.txt", paths, True) == ["a1.txt"]


def test_sorted_matches_no_match_gives_empty_list():
    assert toolkit.match.sorted_matches("*.md", ["b10.txt"]) == []


def test_sorted_matches_minus_sign_is_not_part_of_a_number():
    paths = ["t-10", "t-9", "t5"]
    assert toolkit.match.sorted_matches("t*", paths) == ["t5", "t-9", "t-10"]


def test_sorted_matches_malformed_pattern_raises_even_without_paths():
    with pytest.raises(GlobError):
        toolkit.match.sorted_matches("x\\", [])


# --- re-exports ---------------------------------------------------------


def test_match_facade_exposes_natsort_functions():
    assert toolkit.match.split_chunks("a1") == ["a", "1"]
    assert toolkit.match.natural_key("a1") == ((1, "a"), (0, 1, 1))
    assert toolkit.match.natural_compare("a2", "a10") == -1
    assert toolkit.match.natural_sorted(["a10", "a2"]) == ["a2", "a10"]


def test_match_facade_error_classes_are_the_classes_of_the_modules():
    with pytest.raises(GlobError):
        toolkit.match.glob_match("[", "a")
    with pytest.raises(ScriptError):
        toolkit.match.apply_script("a", [])
    assert toolkit.match.GlobError is GlobError
    assert toolkit.match.ScriptError is ScriptError
