import pytest

from toolkit.containers.pqueue import DuplicateItemError, PriorityQueue


# --- push, pop, peek ----------------------------------------------------


def test_pqueue_new_queue_is_empty():
    queue = PriorityQueue()
    assert len(queue) == 0 and queue.items() == []


def test_pqueue_pop_returns_a_tuple_of_item_and_priority():
    queue = PriorityQueue()
    queue.push("a", 1)
    entry = queue.pop()
    assert type(entry) is tuple and entry == ("a", 1)


def test_pqueue_pop_after_last_entry_raises_index_error():
    queue = PriorityQueue()
    queue.push("a", 1)
    queue.pop()
    with pytest.raises(IndexError):
        queue.pop()


def test_pqueue_negative_and_float_priorities_are_ordered_as_numbers():
    queue = PriorityQueue()
    queue.push("half", 0.5)
    queue.push("minus", -3)
    queue.push("ten", 10)
    queue.push("pi", 3.14)
    assert [item for item, _priority in queue.items()] == ["minus", "half", "pi", "ten"]


def test_pqueue_items_with_equal_priorities_need_not_be_comparable():
    queue = PriorityQueue()
    queue.push(None, 1)
    queue.push("a", 1)
    queue.push((2, 3), 1)
    queue.push(4.5, 1)
    assert [queue.pop()[0] for _ in range(4)] == [None, "a", (2, 3), 4.5]


# --- stability ----------------------------------------------------------


def test_pqueue_int_and_float_priorities_that_are_equal_keep_push_order():
    queue = PriorityQueue()
    queue.push("float", 1.0)
    queue.push("int", 1)
    assert queue.items() == [("float", 1.0), ("int", 1)]


def test_pqueue_many_entries_come_out_sorted_and_stable():
    queue = PriorityQueue()
    for number in range(30):
        queue.push(number, number % 3)
    popped = [queue.pop()[0] for _ in range(30)]
    expected = list(range(0, 30, 3)) + list(range(1, 30, 3)) + list(range(2, 30, 3))
    assert popped == expected


# --- reverse ------------------------------------------------------------


def test_pqueue_reverse_by_position():
    queue = PriorityQueue(True)
    queue.push("low", 1)
    queue.push("high", 9)
    assert queue.peek() == ("high", 9)


# --- duplicates ---------------------------------------------------------


def test_pqueue_push_duplicate_item_raises_duplicate_item_error():
    queue = PriorityQueue()
    queue.push("a", 1)
    with pytest.raises(DuplicateItemError):
        queue.push("a", 2)


def test_pqueue_duplicate_item_error_is_a_value_error():
    queue = PriorityQueue()
    queue.push("a", 1)
    with pytest.raises(ValueError):
        queue.push("a", 2)
    assert issubclass(DuplicateItemError, ValueError)


# --- update -------------------------------------------------------------


def test_pqueue_update_returns_none():
    queue = PriorityQueue()
    queue.push("a", 5)
    assert queue.update("a", 1) is None


def test_pqueue_update_to_same_priority_keeps_the_place():
    queue = PriorityQueue()
    queue.push("a", 2)
    queue.push("b", 2)
    queue.push("c", 2)
    queue.update("a", 2)
    assert queue.items() == [("a", 2), ("b", 2), ("c", 2)]


def test_pqueue_update_does_not_change_the_length():
    queue = PriorityQueue()
    queue.push("a", 2)
    queue.push("b", 3)
    queue.update("a", 7)
    queue.update("a", 1)
    assert len(queue) == 2


def test_pqueue_update_by_keyword_arguments():
    queue = PriorityQueue()
    queue.push(item="a", priority=4)
    queue.update(item="a", priority=6)
    assert queue.priority_of(item="a") == 6


# --- remove, priority_of, in, len ---------------------------------------


def test_pqueue_remove_first_entry_then_pop_gives_the_next():
    queue = PriorityQueue()
    queue.push("a", 1)
    queue.push("b", 2)
    queue.remove("a")
    assert queue.peek() == ("b", 2) and queue.pop() == ("b", 2)


def test_pqueue_removed_item_can_be_pushed_again():
    queue = PriorityQueue()
    queue.push("a", 1)
    queue.push("b", 1)
    queue.remove("a")
    queue.push("a", 1)
    assert queue.items() == [("b", 1), ("a", 1)]


def test_pqueue_contains_true_and_false():
    queue = PriorityQueue()
    queue.push("a", 1)
    assert ("a" in queue) is True and ("b" in queue) is False


# --- items --------------------------------------------------------------


def test_pqueue_items_is_a_list_of_tuples_in_pop_order():
    queue = PriorityQueue()
    queue.push("b", 2)
    queue.push("a", 1)
    items = queue.items()
    assert type(items) is list and type(items[0]) is tuple
    assert items == [("a", 1), ("b", 2)]


# --- priority type ------------------------------------------------------


def test_pqueue_push_string_priority_raises_type_error():
    with pytest.raises(TypeError):
        PriorityQueue().push("a", "1")


def test_pqueue_update_bool_priority_raises_type_error():
    queue = PriorityQueue()
    queue.push("a", 1)
    with pytest.raises(TypeError):
        queue.update("a", False)


