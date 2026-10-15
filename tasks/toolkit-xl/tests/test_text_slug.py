import pytest

from toolkit.text.slug import slugify, slugify_all, unique_slug


# --- slugify ------------------------------------------------------------


def test_slugify_lowercases_and_joins_words_with_hyphens():
    assert slugify("Hello World") == "hello-world"


def test_slugify_removes_accents():
    text = "Cr\u00e8me Br\u00fbl\u00e9e \u00e0 la carte"
    assert slugify(text) == "creme-brulee-a-la-carte"


def test_slugify_keeps_digits():
    assert slugify("Python 3.12 released") == "python-3-12-released"


def test_slugify_text_without_ascii_letters_or_digits_gives_empty_string():
    assert slugify("\u65e5\u672c\u8a9e ???") == ""


def test_slugify_underscore_separator():
    assert slugify("Hello big World", separator="_") == "hello_big_world"


def test_slugify_invalid_separator_raises_value_error():
    with pytest.raises(ValueError):
        slugify("Hello World", separator="+")


def test_slugify_max_length_removes_trailing_separator_after_cut():
    assert slugify("alpha beta gamma", max_length=6) == "alpha"


def test_slugify_max_length_below_one_raises_value_error():
    with pytest.raises(ValueError):
        slugify("alpha", max_length=0)


# --- unique_slug --------------------------------------------------------


def test_unique_slug_uses_smallest_free_number():
    taken = {"my-post", "my-post-2", "my-post-3", "my-post-5"}
    assert unique_slug("My Post", taken) == "my-post-4"


def test_unique_slug_untitled_is_numbered_too():
    assert unique_slug("", ["untitled", "untitled-2"]) == "untitled-3"


def test_unique_slug_invalid_separator_raises_value_error():
    with pytest.raises(ValueError):
        unique_slug("My Post", [], separator=" ")


# --- slugify_all --------------------------------------------------------


def test_slugify_all_duplicate_skips_number_taken_by_earlier_text():
    assert slugify_all(["a", "a 2", "a"]) == ["a", "a-2", "a-3"]


def test_slugify_all_with_underscore_separator():
    assert slugify_all(["a b", "a b"], separator="_") == ["a_b", "a_b_2"]


