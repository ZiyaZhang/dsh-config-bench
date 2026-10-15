import pytest

from toolkit.containers.ring import BufferFullError, RingBuffer, window_stats


# --- construction -------------------------------------------------------


def test_ring_new_buffer_is_empty():
    buffer = RingBuffer(3)
    assert len(buffer) == 0 and buffer.to_list() == [] and buffer.is_full() is False


def test_ring_capacity_zero_raises_value_error():
    with pytest.raises(ValueError):
        RingBuffer(0)


# --- append -------------------------------------------------------------


def test_ring_append_returns_none():
    buffer = RingBuffer(2)
    assert buffer.append("a") is None


def test_ring_append_overwriting_keeps_the_length():
    buffer = RingBuffer(2)
    for value in range(7):
        buffer.append(value)
    assert len(buffer) == 2 and buffer.to_list() == [5, 6]


def test_ring_append_to_full_strict_buffer_raises_buffer_full_error():
    buffer = RingBuffer(2, overwrite=False)
    buffer.append(1)
    buffer.append(2)
    with pytest.raises(BufferFullError):
        buffer.append(3)


def test_ring_strict_buffer_accepts_values_again_after_popleft():
    buffer = RingBuffer(2, overwrite=False)
    buffer.append(1)
    buffer.append(2)
    buffer.popleft()
    buffer.append(3)
    assert buffer.to_list() == [2, 3]


# --- extend -------------------------------------------------------------


def test_ring_extend_returns_zero_when_nothing_is_dropped():
    buffer = RingBuffer(5)
    result = buffer.extend([1, 2, 3])
    assert result == 0 and type(result) is int


def test_ring_extend_accepts_a_generator():
    buffer = RingBuffer(3)
    buffer.extend(number * 2 for number in range(4))
    assert buffer.to_list() == [2, 4, 6]


def test_ring_extend_strict_buffer_too_many_raises_buffer_full_error():
    buffer = RingBuffer(3, overwrite=False)
    buffer.append(1)
    with pytest.raises(BufferFullError):
        buffer.extend([2, 3, 4])


# --- popleft ------------------------------------------------------------


def test_ring_popleft_on_empty_buffer_raises_index_error():
    with pytest.raises(IndexError):
        RingBuffer(3).popleft()


def test_ring_popleft_makes_the_buffer_not_full():
    buffer = RingBuffer(2)
    buffer.extend([1, 2])
    buffer.popleft()
    assert buffer.is_full() is False


# --- indexing -----------------------------------------------------------


def test_ring_negative_index_counts_from_the_newest():
    buffer = RingBuffer(3)
    buffer.extend([1, 2, 3, 4])
    assert buffer[-1] == 4 and buffer[-3] == 2


def test_ring_index_into_empty_buffer_raises_index_error():
    buffer = RingBuffer(3)
    with pytest.raises(IndexError):
        buffer[0]


def test_ring_string_index_raises_type_error():
    buffer = RingBuffer(3)
    buffer.extend([1, 2, 3])
    with pytest.raises(TypeError):
        buffer["0"]


# --- iteration ----------------------------------------------------------


def test_ring_iteration_of_empty_buffer_gives_nothing():
    assert list(RingBuffer(2)) == []


# --- len, is_full, to_list, clear ---------------------------------------


def test_ring_len_grows_up_to_capacity():
    buffer = RingBuffer(2)
    lengths = []
    for value in range(4):
        buffer.append(value)
        lengths.append(len(buffer))
    assert lengths == [1, 2, 2, 2]


def test_ring_clear_removes_all_values():
    buffer = RingBuffer(3)
    buffer.extend([1, 2, 3, 4])
    assert buffer.clear() is None
    assert len(buffer) == 0 and buffer.to_list() == [] and buffer.is_full() is False


# --- window_stats -------------------------------------------------------


def test_window_stats_full_windows_only_by_default():
    assert window_stats([4, 8, 6, 2], 2) == [(4, 8, 6.0), (6, 8, 7.0), (2, 6, 4.0)]


def test_window_stats_number_of_windows_with_partial():
    assert len(window_stats(range(10), 4, True)) == 10


def test_window_stats_size_one_gives_each_value():
    assert window_stats([3, 1, 2], 1) == [(3, 3, 3.0), (1, 1, 1.0), (2, 2, 2.0)]


def test_window_stats_negative_size_raises_value_error():
    with pytest.raises(ValueError):
        window_stats([], -1)


def test_window_stats_window_slides_by_one_value():
    result = window_stats([5, 1, 9, 3, 7], size=3)
    assert [(low, high) for low, high, _mean in result] == [(1, 9), (1, 9), (3, 9)]
    assert result[0][2] == pytest.approx(5.0, rel=1e-9, abs=1e-9)
    assert result[2][2] == pytest.approx(19 / 3, rel=1e-9, abs=1e-9)


