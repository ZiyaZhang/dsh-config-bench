import pytest

import toolkit.containers
from toolkit.containers.lru import LRUCache
from toolkit.containers.pqueue import DuplicateItemError, PriorityQueue
from toolkit.containers.ring import BufferFullError, RingBuffer
from toolkit.containers.trie import Trie


# --- suggest ------------------------------------------------------------


def test_suggest_ranks_by_count():
    words = ["cat", "car", "car", "cab", "car", "cab"]
    assert toolkit.containers.suggest(words, "ca") == [("car", 3), ("cab", 2), ("cat", 1)]


def test_suggest_equal_counts_same_length_in_code_point_order():
    words = ["cot", "cat", "cut", "Cat"]
    assert toolkit.containers.suggest(words, "") == [("Cat", 1), ("cat", 1), ("cot", 1), ("cut", 1)]


def test_suggest_default_limit_is_five():
    words = ["a1", "a2", "a3", "a4", "a5", "a6", "a7"]
    assert toolkit.containers.suggest(words, "a") == [
        ("a1", 1),
        ("a2", 1),
        ("a3", 1),
        ("a4", 1),
        ("a5", 1),
    ]


def test_suggest_limit_zero_gives_empty_list():
    assert toolkit.containers.suggest(["car", "cat"], "ca", limit=0) == []


def test_suggest_empty_words_give_empty_list():
    assert toolkit.containers.suggest([], "") == []


def test_suggest_non_string_word_raises_type_error():
    with pytest.raises(TypeError):
        toolkit.containers.suggest(["car", 5], "ca")


# --- re-exports ---------------------------------------------------------


def test_containers_facade_exposes_lru_cache():
    cache = toolkit.containers.LRUCache(1)
    cache.put("a", 1)
    assert cache.put("b", 2) == ("a", 1)
    assert toolkit.containers.LRUCache is LRUCache


def test_containers_facade_exposes_trie():
    trie = toolkit.containers.Trie(["ab", "a"])
    assert trie.with_prefix("") == ["a", "ab"]
    assert toolkit.containers.Trie is Trie


