import pytest

from toolkit.calc.intervals import (
    count_points,
    intersect_intervals,
    merge_intervals,
    subtract_intervals,
)


# --- merge_intervals ----------------------------------------------------


def test_merge_empty_list_gives_empty_list():
    assert merge_intervals([]) == []


def test_merge_adjacent_intervals_are_joined():
    assert merge_intervals([(1, 2), (3, 4)]) == [(1, 4)]


def test_merge_contained_interval_disappears():
    assert merge_intervals([(1, 10), (3, 4)]) == [(1, 10)]


def test_merge_single_point_intervals_join_when_adjacent():
    assert merge_intervals([(3, 3), (5, 5), (4, 4)]) == [(3, 5)]


def test_merge_accepts_tuple_of_intervals():
    assert merge_intervals(((1, 2), (2, 3))) == [(1, 3)]


# --- intersect_intervals ------------------------------------------------


def test_intersect_overlapping_intervals():
    assert intersect_intervals([(1, 5)], [(3, 8)]) == [(3, 5)]


def test_intersect_shared_end_point_gives_single_point():
    assert intersect_intervals([(1, 4)], [(4, 9)]) == [(4, 4)]


def test_intersect_several_intervals_on_both_sides():
    result = intersect_intervals([(1, 3), (6, 8), (11, 15)], [(2, 7), (12, 20)])
    assert result == [(2, 3), (6, 7), (12, 15)]


def test_intersect_result_has_no_adjacent_pieces():
    assert intersect_intervals([(1, 3), (4, 6)], [(2, 5)]) == [(2, 5)]


# --- subtract_intervals -------------------------------------------------


def test_subtract_cut_in_the_middle_gives_two_pieces():
    assert subtract_intervals([(1, 10)], [(4, 6)]) == [(1, 3), (7, 10)]


def test_subtract_trims_right_edge():
    assert subtract_intervals([(1, 5)], [(5, 8)]) == [(1, 4)]


def test_subtract_cut_ending_at_interval_end():
    assert subtract_intervals([(5, 9)], [(8, 9)]) == [(5, 7)]


def test_subtract_several_cuts():
    result = subtract_intervals([(1, 20)], [(3, 4), (8, 8), (15, 30)])
    assert result == [(1, 2), (5, 7), (9, 14)]


def test_subtract_invalid_interval_raises_value_error():
    with pytest.raises(ValueError):
        subtract_intervals([(4, 1)], [])


# --- count_points -------------------------------------------------------


def test_count_points_overlap_counts_once():
    assert count_points([(1, 5), (4, 8)]) == 8


def test_count_points_with_negative_numbers():
    assert count_points([(-3, 3)]) == 7


