import pytest

from toolkit.containers.lru import LRUCache


# --- construction -------------------------------------------------------


def test_lru_new_cache_is_empty():
    cache = LRUCache(3)
    assert len(cache) == 0 and cache.items() == [] and cache.keys() == []


def test_lru_capacity_zero_raises_value_error():
    with pytest.raises(ValueError):
        LRUCache(0)


# --- put ----------------------------------------------------------------


def test_lru_put_new_key_returns_none():
    cache = LRUCache(2)
    assert cache.put("a", 1) is None


def test_lru_put_evicted_entry_is_a_tuple():
    cache = LRUCache(1)
    cache.put("a", 1)
    evicted = cache.put("b", 2)
    assert type(evicted) is tuple


def test_lru_put_existing_key_replaces_value():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("a", 2)
    assert cache.items() == [("a", 2)]


def test_lru_put_existing_key_counts_as_use():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 10)
    assert cache.put("c", 3) == ("b", 2)


def test_lru_keys_are_compared_like_dict_keys():
    cache = LRUCache(3)
    cache.put(1, "int")
    cache.put(1.0, "float")
    assert len(cache) == 1 and cache.peek(1) == "float"


# --- get ----------------------------------------------------------------


def test_lru_get_missing_key_returns_none_by_default():
    cache = LRUCache(2)
    assert cache.get("a") is None


def test_lru_get_counts_as_use():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")
    assert cache.put("c", 3) == ("b", 2)


def test_lru_get_miss_does_not_change_the_order():
    cache = LRUCache(3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("zzz")
    assert cache.keys() == ["b", "a"] and len(cache) == 2


# --- peek ---------------------------------------------------------------


def test_lru_peek_missing_key_returns_none_by_default():
    assert LRUCache(2).peek("a") is None


def test_lru_peek_does_not_change_the_counters():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.peek("a")
    cache.peek("b")
    assert cache.stats() == {"hits": 0, "misses": 0, "evictions": 0}


# --- in, len ------------------------------------------------------------


def test_lru_contains_does_not_change_the_counters():
    cache = LRUCache(2)
    cache.put("a", 1)
    assert "a" in cache and "b" not in cache
    assert cache.stats() == {"hits": 0, "misses": 0, "evictions": 0}


# --- pop ----------------------------------------------------------------


def test_lru_pop_missing_key_raises_key_error():
    cache = LRUCache(2)
    cache.put("a", 1)
    with pytest.raises(KeyError):
        cache.pop("b")


def test_lru_pop_makes_room_for_a_new_entry():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.pop("a")
    assert cache.put("c", 3) is None
    assert cache.keys() == ["c", "b"]


# --- keys, items --------------------------------------------------------


def test_lru_items_is_a_list_of_tuples():
    cache = LRUCache(2)
    cache.put("a", 1)
    items = cache.items()
    assert type(items) is list and type(items[0]) is tuple
    assert type(cache.keys()) is list


# --- resize -------------------------------------------------------------


def test_lru_resize_smaller_evicts_least_recently_used_first():
    cache = LRUCache(4)
    for key, value in [("a", 1), ("b", 2), ("c", 3), ("d", 4)]:
        cache.put(key, value)
    assert cache.resize(2) == [("a", 1), ("b", 2)]
    assert cache.keys() == ["d", "c"]


def test_lru_resize_larger_allows_more_entries():
    cache = LRUCache(1)
    cache.put("a", 1)
    cache.resize(2)
    assert cache.put("b", 2) is None
    assert len(cache) == 2


def test_lru_resize_rejected_leaves_the_cache_unchanged():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    with pytest.raises(ValueError):
        cache.resize(-1)
    assert cache.capacity == 2 and cache.items() == [("b", 2), ("a", 1)]


# --- clear --------------------------------------------------------------


def test_lru_clear_returns_the_number_of_removed_entries():
    cache = LRUCache(3)
    cache.put("a", 1)
    cache.put("b", 2)
    result = cache.clear()
    assert result == 2 and type(result) is int


def test_lru_clear_is_not_an_eviction_and_keeps_the_counters():
    cache = LRUCache(1)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("b")
    cache.get("a")
    cache.clear()
    assert cache.stats() == {"hits": 1, "misses": 1, "evictions": 1}


# --- stats --------------------------------------------------------------


def test_lru_stats_is_a_dict_with_three_keys():
    stats = LRUCache(2).stats()
    assert type(stats) is dict and sorted(stats) == ["evictions", "hits", "misses"]


def test_lru_stats_put_is_neither_hit_nor_miss():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("a", 2)
    assert cache.stats() == {"hits": 0, "misses": 0, "evictions": 0}
