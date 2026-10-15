import pytest

from toolkit.geom.hull import bounding_box, convex_hull, diameter, farthest_pair


# --- convex_hull: corners -----------------------------------------------


def test_convex_hull_drops_points_inside():
    points = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (1, 3)]
    assert convex_hull(points) == [(0, 0), (4, 0), (4, 4), (0, 4)]


def test_convex_hull_among_the_lowest_points_starts_at_the_leftmost():
    assert convex_hull([(3, 0), (1, 0), (2, 5)]) == [(1, 0), (3, 0), (2, 5)]


def test_convex_hull_with_negative_coordinates():
    points = [(1, 1), (-1, 1), (0, 0), (-1, -1), (1, -1)]
    assert convex_hull(points) == [(-1, -1), (1, -1), (1, 1), (-1, 1)]


def test_convex_hull_keeps_int_coordinates():
    result = convex_hull([(0, 0), (1, 0), (0, 1)])
    assert [type(value) for point in result for value in point] == [int] * 6


# --- convex_hull: repeated points and points on an edge -----------------


def test_convex_hull_point_on_an_edge_is_left_out():
    points = [(0, 0), (2, 0), (4, 0), (4, 3), (0, 3)]
    assert convex_hull(points) == [(0, 0), (4, 0), (4, 3), (0, 3)]


def test_convex_hull_without_keep_collinear_on_all_four_edges():
    points = [(1, 1), (0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1)]
    assert convex_hull(points) == [(0, 0), (2, 0), (2, 2), (0, 2)]


def test_convex_hull_keep_collinear_counts_repeated_points_once():
    points = [(0, 0), (2, 0), (2, 0), (4, 0), (0, 3)]
    assert convex_hull(points, keep_collinear=True) == [(0, 0), (2, 0), (4, 0), (0, 3)]


# --- convex_hull: fewer than three corners ------------------------------


def test_convex_hull_of_equal_points_is_one_point():
    assert convex_hull([(5, 5), (5, 5), (5, 5)], keep_collinear=True) == [(5, 5)]


def test_convex_hull_of_points_on_one_line_is_its_two_ends():
    assert convex_hull([(3, 3), (1, 1), (2, 2)]) == [(1, 1), (3, 3)]


def test_convex_hull_of_points_on_a_falling_line_with_keep_collinear():
    assert convex_hull([(0, 4), (4, 0), (1, 3), (2, 2)], keep_collinear=True) == [
        (4, 0),
        (2, 2),
        (1, 3),
        (0, 4),
    ]


def test_convex_hull_of_points_on_a_vertical_line():
    assert convex_hull([(1, 3), (1, 5), (1, 1)]) == [(1, 1), (1, 5)]


# --- bounding_box -------------------------------------------------------


def test_bounding_box_of_one_point():
    assert bounding_box([(3, 7)]) == ((3, 7), (3, 7))


def test_bounding_box_keeps_int_coordinates():
    result = bounding_box([(1, 5), (-2, 3)])
    assert [type(value) for point in result for value in point] == [int] * 4


# --- farthest_pair ------------------------------------------------------


def test_farthest_pair_of_four_points():
    assert farthest_pair([(0, 0), (3, 4), (-3, -4), (1, 1)]) == ((-3, -4), (3, 4))


def test_farthest_pair_tie_takes_the_pair_with_the_smallest_first_point():
    assert farthest_pair([(2, 2), (2, 0), (0, 2), (0, 0)]) == ((0, 0), (2, 2))


def test_farthest_pair_wide_and_flat():
    assert farthest_pair([(0, 0), (5, 1), (1, 3)]) == ((0, 0), (5, 1))


def test_farthest_pair_of_one_point_is_that_point_twice():
    assert farthest_pair([(7, 7)]) == ((7, 7), (7, 7))


def test_farthest_pair_with_float_coordinates():
    assert farthest_pair([(0.5, 0.5), (0.25, 0.5), (2.5, 0.5)]) == ((0.25, 0.5), (2.5, 0.5))


# --- diameter -----------------------------------------------------------


def test_diameter_of_four_points():
    points = [(0, 0), (3, 4), (-3, -4), (1, 1)]
    assert diameter(points) == pytest.approx(10.0, rel=1e-9, abs=1e-9)


def test_diameter_of_one_point_is_a_float_zero():
    result = diameter([(7, 7)])
    assert type(result) is float and result == 0.0


def test_diameter_of_no_points_raises_value_error():
    with pytest.raises(ValueError):
        diameter([])
