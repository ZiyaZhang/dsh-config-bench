import pytest

from toolkit.match.editdist import (
    ScriptError,
    apply_script,
    closest_matches,
    damerau,
    edit_script,
    levenshtein,
)


# --- levenshtein --------------------------------------------------------


def test_levenshtein_equal_strings_is_zero():
    assert levenshtein("same", "same") == 0


def test_levenshtein_one_substitution():
    assert levenshtein("cat", "cut") == 1


def test_levenshtein_kitten_sitting():
    assert levenshtein("kitten", "sitting") == 3


def test_levenshtein_is_symmetric():
    assert levenshtein("sunday", "saturday") == 3
    assert levenshtein("saturday", "sunday") == 3


def test_levenshtein_result_is_an_int():
    assert type(levenshtein("a", "b")) is int


# --- damerau ------------------------------------------------------------


def test_damerau_swap_of_neighbours_costs_one():
    assert damerau("ab", "ba") == 1


def test_damerau_from_empty_is_length_of_other():
    assert damerau("", "abc") == 3
    assert damerau("ab", "") == 2


def test_damerau_without_swaps_equals_levenshtein():
    assert damerau("kitten", "sitting") == 3


def test_damerau_two_separate_swaps():
    assert damerau("abcd", "badc") == 2


def test_damerau_nothing_is_inserted_between_swapped_characters():
    assert damerau("ab", "bxa") == 3


# --- edit_script --------------------------------------------------------


def test_edit_script_of_empty_strings_is_empty():
    assert edit_script("", "") == []


def test_edit_script_to_empty_is_all_deletions():
    assert edit_script("ab", "") == [("del", "a"), ("del", "b")]


def test_edit_script_deletion_at_the_start():
    assert edit_script("abc", "bc") == [("del", "a"), ("keep", "b"), ("keep", "c")]


def test_edit_script_prefers_substitution_when_shifting_is_as_short():
    assert edit_script("ab", "bc") == [("sub", "a", "b"), ("sub", "b", "c")]


def test_edit_script_substitution_first_when_lengths_differ():
    assert edit_script("ab", "c") == [("sub", "a", "c"), ("del", "b")]


def test_edit_script_repeated_characters_in_target():
    assert edit_script("ab", "aab") == [("keep", "a"), ("ins", "a"), ("keep", "b")]


def test_edit_script_steps_are_tuples_in_a_list():
    script = edit_script("a", "b")
    assert type(script) is list and type(script[0]) is tuple


# --- apply_script -------------------------------------------------------


def test_apply_script_reproduces_the_target_of_edit_script():
    assert apply_script("kitten", edit_script("kitten", "sitting")) == "sitting"
    assert apply_script("sunday", edit_script("sunday", "saturday")) == "saturday"


def test_apply_script_insertion_after_the_last_character():
    assert apply_script("a", [("keep", "a"), ("ins", "b")]) == "ab"


def test_apply_script_substitution_of_wrong_character_raises_script_error():
    with pytest.raises(ScriptError):
        apply_script("a", [("sub", "b", "a")])


def test_apply_script_unknown_step_raises_script_error():
    with pytest.raises(ScriptError):
        apply_script("a", [("swap", "a")])


# --- closest_matches ----------------------------------------------------


def test_closest_matches_default_max_distance_is_two():
    assert closest_matches("abcd", ["abcd", "abc", "ab", "a"]) == ["abcd", "abc", "ab"]


def test_closest_matches_equal_distances_keep_input_order():
    assert closest_matches("b", ["c", "a", "bb", "", "d"], 1) == ["c", "a", "bb", "", "d"]


def test_closest_matches_is_case_sensitive():
    assert closest_matches("cat", ["CAT", "dog"], 2) == []


def test_closest_matches_large_max_distance_keeps_everything_sorted():
    assert closest_matches("a", ["xyz", "a", "ab"], 10) == ["a", "ab", "xyz"]


