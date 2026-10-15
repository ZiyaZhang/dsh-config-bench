import pytest

from toolkit.containers.trie import Trie


# --- construction, insert, in, len --------------------------------------


def test_trie_new_trie_is_empty():
    trie = Trie()
    assert len(trie) == 0 and trie.with_prefix("") == [] and trie.node_count() == 0


def test_trie_constructor_by_keyword():
    trie = Trie(words=("x", "y"))
    assert trie.with_prefix("") == ["x", "y"]


def test_trie_insert_twice_counts_once():
    trie = Trie()
    trie.insert("tea")
    trie.insert("tea")
    assert len(trie) == 1 and trie.count_prefix("t") == 1


def test_trie_is_case_sensitive():
    trie = Trie(["Tea"])
    assert "tea" not in trie and trie.has_prefix("t") is False and "Tea" in trie


def test_trie_prefix_and_longer_word_are_both_stored():
    trie = Trie(["team", "tea"])
    assert "tea" in trie and "team" in trie and len(trie) == 2


# --- has_prefix, count_prefix -------------------------------------------


def test_trie_has_prefix_false_for_other_text():
    trie = Trie(["team"])
    assert trie.has_prefix("tex") is False and trie.has_prefix("teams") is False


def test_trie_has_prefix_empty_string_after_removing_everything_is_false():
    trie = Trie(["a"])
    trie.remove("a")
    assert trie.has_prefix("") is False and trie.has_prefix("a") is False


def test_trie_count_prefix_of_unknown_prefix_is_zero():
    trie = Trie(["tea"])
    result = trie.count_prefix("x")
    assert result == 0 and type(result) is int


# --- with_prefix --------------------------------------------------------


def test_trie_with_prefix_shorter_words_come_first():
    trie = Trie(["abc", "b", "ab"])
    assert trie.with_prefix("") == ["b", "ab", "abc"]


def test_trie_with_prefix_order_is_not_plain_sorted_order():
    trie = Trie(["car", "cat", "ca", "cart", "cab", "c"])
    assert trie.with_prefix("c") == ["c", "ca", "cab", "car", "cat", "cart"]


def test_trie_with_prefix_no_match_gives_empty_list():
    assert Trie(["tea"]).with_prefix("x") == []


def test_trie_with_prefix_limit_takes_the_first_words():
    trie = Trie(["tea", "ten", "to", "team", "inn", "i"])
    assert trie.with_prefix("", limit=3) == ["i", "to", "inn"]


def test_trie_with_prefix_limit_larger_than_matches_gives_all():
    assert Trie(["tea", "to"]).with_prefix("t", limit=10) == ["to", "tea"]


# --- longest_prefix -----------------------------------------------------


def test_trie_longest_prefix_finds_the_longest_stored_word():
    trie = Trie(["t", "tea", "team"])
    assert trie.longest_prefix("teammate") == "team"


def test_trie_longest_prefix_none_when_nothing_matches():
    trie = Trie(["tea"])
    assert trie.longest_prefix("coffee") is None


def test_trie_longest_prefix_of_empty_text():
    assert Trie(["a"]).longest_prefix("") is None
    assert Trie(["", "a"]).longest_prefix("") == ""


# --- remove -------------------------------------------------------------


def test_trie_remove_unknown_word_returns_false():
    trie = Trie(["tea"])
    assert trie.remove("coffee") is False and len(trie) == 1


def test_trie_remove_keeps_longer_words():
    trie = Trie(["tea", "team"])
    trie.remove("tea")
    assert "team" in trie and "tea" not in trie and trie.with_prefix("") == ["team"]


def test_trie_remove_makes_unused_prefixes_disappear():
    trie = Trie(["tea", "team"])
    trie.remove("team")
    assert trie.has_prefix("team") is False and trie.has_prefix("tea") is True


# --- node_count ---------------------------------------------------------


def test_trie_node_count_counts_distinct_prefixes():
    trie = Trie(["tea", "ten", "to", "team", "inn", "i"])
    assert trie.node_count() == 9


def test_trie_node_count_ignores_the_empty_word():
    assert Trie([""]).node_count() == 0


def test_trie_node_count_prunes_a_whole_branch():
    trie = Trie(["a", "abcde"])
    trie.remove("abcde")
    assert trie.node_count() == 1


# --- types --------------------------------------------------------------


def test_trie_constructor_with_non_string_raises_type_error():
    with pytest.raises(TypeError):
        Trie(["ok", b"bytes"])


def test_trie_longest_prefix_non_string_raises_type_error():
    with pytest.raises(TypeError):
        Trie(["a"]).longest_prefix(["a"])


