import pytest

from toolkit.match.natsort import (
    natural_compare,
    natural_key,
    natural_sorted,
    split_chunks,
)


# --- split_chunks -------------------------------------------------------


def test_split_chunks_text_and_number_runs_alternate():
    assert split_chunks("img012b7") == ["img", "012", "b", "7"]


def test_split_chunks_only_digits():
    assert split_chunks("2024") == ["2024"]


def test_split_chunks_minus_is_text_by_default():
    assert split_chunks("-5") == ["-", "5"]


def test_split_chunks_non_ascii_digits_are_text():
    assert split_chunks("x\u00b2y\u0663z1") == ["x\u00b2y\u0663z", "1"]


def test_split_chunks_signed_minus_after_tab_belongs_to_number():
    assert split_chunks("a\t-12b", True) == ["a\t", "-12", "b"]


def test_split_chunks_signed_double_minus_stays_text():
    assert split_chunks("--5", signed=True) == ["--", "5"]


def test_split_chunks_non_string_raises_type_error():
    with pytest.raises(TypeError):
        split_chunks(15)


# --- natural_key --------------------------------------------------------


def test_natural_key_is_a_tuple_of_tuples():
    key = natural_key("a1")
    assert type(key) is tuple and key == ((1, "a"), (0, 1, 1))


def test_natural_key_example():
    assert natural_key("img012b-7.png") == (
        (1, "img"),
        (0, 12, 3),
        (1, "b-"),
        (0, 7, 1),
        (1, ".png"),
    )


def test_natural_key_ignore_case_uses_casefold():
    assert natural_key("Stra\u00dfe", True) == ((1, "strasse"),)


def test_natural_key_signed_in_the_middle():
    assert natural_key("t -3x", False, True) == ((1, "t "), (0, -3, 1), (1, "x"))


def test_natural_key_non_string_raises_type_error():
    with pytest.raises(TypeError):
        natural_key(None)


# --- natural_compare ----------------------------------------------------


def test_natural_compare_fewer_leading_zeros_first():
    assert natural_compare("a1", "a01") == -1
    assert natural_compare("a001", "a01") == 1


def test_natural_compare_prefix_comes_first():
    assert natural_compare("a", "a1") == -1
    assert natural_compare("a1b", "a1") == 1
    assert natural_compare("", "0") == -1


def test_natural_compare_case_difference_without_ignore_case():
    assert natural_compare("File1", "file1") == -1


# --- natural_sorted -----------------------------------------------------


def test_natural_sorted_orders_numbers_by_value():
    assert natural_sorted(["f10", "f9", "f100", "f1"]) == ["f1", "f9", "f10", "f100"]


def test_natural_sorted_returns_new_list_and_keeps_input():
    names = ["b2", "b10", "a1"]
    result = natural_sorted(names)
    assert result == ["a1", "b2", "b10"] and names == ["b2", "b10", "a1"]
    assert result is not names


def test_natural_sorted_versions():
    assert natural_sorted(["1.10", "1.9", "1.5", "1.10.1"]) == ["1.5", "1.9", "1.10", "1.10.1"]


def test_natural_sorted_numbers_before_letters():
    assert natural_sorted(["b", "10", "a", "9"]) == ["9", "10", "a", "b"]


def test_natural_sorted_reverse():
    assert natural_sorted(["f10", "f9", "f100"], reverse=True) == ["f100", "f10", "f9"]


def test_natural_sorted_key_as_second_positional_argument():
    assert natural_sorted([10, 9, 100], str) == [9, 10, 100]


