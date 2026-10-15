import pytest

from toolkit.geom.segment import (
    midpoint,
    point_on_segment,
    point_segment_distance,
    segment_intersection,
    segment_length,
    segments_intersect,
    turn,
)


# --- segment_length, midpoint -------------------------------------------


def test_segment_length_of_a_three_four_five_triangle_side():
    assert segment_length(((0, 0), (3, 4))) == pytest.approx(5.0, rel=1e-9, abs=1e-9)


def test_segment_length_accepts_lists():
    assert segment_length([[1, 1], [1, -6]]) == pytest.approx(7.0, rel=1e-9, abs=1e-9)


def test_midpoint_of_a_single_point():
    assert midpoint([(3, 5), (3, 5)]) == (3.0, 5.0)


# --- turn ---------------------------------------------------------------


def test_turn_right_is_minus_one():
    assert turn((0, 0), (1, 0), (1, -1)) == -1


def test_turn_with_equal_points_is_zero():
    assert turn((1, 1), (1, 1), (5, 7)) == 0


# --- point_on_segment ---------------------------------------------------


def test_point_on_segment_inner_point():
    assert point_on_segment((1, 1), ((0, 0), (2, 2))) is True


def test_point_on_segment_point_beside_the_line():
    assert point_on_segment((1, 2), ((0, 0), (2, 2))) is False


def test_point_on_segment_on_a_segment_given_from_right_to_left():
    assert point_on_segment((6, 2), ((9, 1), (3, 3))) is True


def test_point_on_segment_beyond_the_end_in_general_position():
    assert point_on_segment((9, 6), ((1, 2), (7, 5))) is False


def test_point_on_segment_horizontal_segment():
    assert point_on_segment((-1, 2), ((-4, 2), (3, 2))) is True


def test_point_on_segment_float_coordinates():
    assert point_on_segment((0.5, 0.25), ((0, 0), (2, 1))) is True


# --- point_segment_distance ---------------------------------------------


def test_point_segment_distance_perpendicular_foot_on_the_segment():
    result = point_segment_distance((4, 5), ((0, 0), (10, 0)))
    assert result == pytest.approx(5.0, rel=1e-9, abs=1e-9)


def test_point_segment_distance_in_general_position():
    result = point_segment_distance((4, 7), ((1, 2), (7, 5)))
    assert result == pytest.approx(3.1304951684997055, rel=1e-9, abs=1e-9)


def test_point_segment_distance_of_a_point_on_the_segment_is_zero():
    result = point_segment_distance((1, 1), ((0, 0), (2, 2)))
    assert result == pytest.approx(0.0, rel=1e-9, abs=1e-9)


def test_point_segment_distance_result_is_a_float():
    assert type(point_segment_distance((0, 0), ((0, 0), (1, 0)))) is float


# --- segment_intersection: one point ------------------------------------


def test_segment_intersection_crossing_point_with_fractions():
    result = segment_intersection(((0, 0), (3, 1)), ((0, 1), (3, 0)))
    assert result == pytest.approx((1.5, 0.5), rel=1e-9, abs=1e-9)


def test_segment_intersection_crossing_with_the_first_segment_reversed():
    result = segment_intersection(((7, 5), (1, 2)), ((2, 6), (6, 1)))
    assert result == pytest.approx((4.0, 3.5), rel=1e-9, abs=1e-9)


def test_segment_intersection_crossing_away_from_the_middle():
    result = segment_intersection(((1, 1), (9, 5)), ((2, 4), (4, 0)))
    assert result == pytest.approx((3.0, 2.0), rel=1e-9, abs=1e-9)


def test_segment_intersection_end_point_touches_the_inside_of_the_other():
    result = segment_intersection(((0, 0), (4, 0)), ((1, 0), (1, 3)))
    assert result == pytest.approx((1.0, 0.0), rel=1e-9, abs=1e-9)


def test_segment_intersection_start_point_touches_the_inside_of_the_other():
    result = segment_intersection(((1, 0), (1, 3)), ((0, 0), (4, 0)))
    assert result == pytest.approx((1.0, 0.0), rel=1e-9, abs=1e-9)


def test_segment_intersection_touching_in_general_position():
    result = segment_intersection(((1, 2), (7, 5)), ((5, 4), (6, 9)))
    assert result == pytest.approx((5.0, 4.0), rel=1e-9, abs=1e-9)


# --- segment_intersection: no common point ------------------------------


def test_segment_intersection_lines_cross_outside_both_segments():
    assert segment_intersection(((0, 0), (1, 1)), ((3, 0), (4, -1))) is None


def test_segment_intersection_line_meets_the_other_one_unit_after_its_end():
    assert segment_intersection(((0, 0), (0, 1)), ((1, 0), (2, 0))) is None


def test_segment_intersection_segments_on_one_line_apart():
    assert segment_intersection(((0, 0), (1, 1)), ((2, 2), (3, 3))) is None


# --- segment_intersection: segments on one line -------------------------


def test_segment_intersection_overlap_is_a_tuple_of_tuples_of_floats():
    result = segment_intersection(((0, 0), (4, 0)), ((2, 0), (6, 0)))
    assert type(result) is tuple and type(result[0]) is tuple and type(result[1]) is tuple
    assert [type(value) for point in result for value in point] == [float] * 4


def test_segment_intersection_overlap_on_a_falling_line_is_ordered_by_x():
    first, second = segment_intersection(((0, 4), (4, 0)), ((3, 1), (1, 3)))
    assert first == pytest.approx((1.0, 3.0), rel=1e-9, abs=1e-9)
    assert second == pytest.approx((3.0, 1.0), rel=1e-9, abs=1e-9)


def test_segment_intersection_identical_segments():
    first, second = segment_intersection(((0, 0), (2, 2)), ((0, 0), (2, 2)))
    assert first == pytest.approx((0.0, 0.0), rel=1e-9, abs=1e-9)
    assert second == pytest.approx((2.0, 2.0), rel=1e-9, abs=1e-9)


def test_segment_intersection_touching_on_one_line_is_a_point():
    result = segment_intersection(((0, 0), (2, 0)), ((2, 0), (5, 0)))
    assert result == pytest.approx((2.0, 0.0), rel=1e-9, abs=1e-9)


# --- segment_intersection: single points --------------------------------


def test_segment_intersection_single_point_as_second_argument():
    result = segment_intersection(((0, 0), (2, 2)), ((1, 1), (1, 1)))
    assert result == pytest.approx((1.0, 1.0), rel=1e-9, abs=1e-9)


def test_segment_intersection_single_point_at_an_end_point():
    result = segment_intersection(((2, 2), (2, 2)), ((0, 0), (2, 2)))
    assert result == pytest.approx((2.0, 2.0), rel=1e-9, abs=1e-9)


def test_segment_intersection_two_equal_single_points():
    result = segment_intersection(((1, 2), (1, 2)), ((1, 2), (1, 2)))
    assert result == pytest.approx((1.0, 2.0), rel=1e-9, abs=1e-9)


# --- segments_intersect -------------------------------------------------


def test_segments_intersect_parallel():
    assert segments_intersect(((0, 0), (1, 0)), ((0, 1), (1, 1))) is False


def test_segments_intersect_on_one_line_apart():
    assert segments_intersect(((0, 0), (1, 1)), ((2, 2), (3, 3))) is False
