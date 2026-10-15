import pytest

from toolkit.geom.polygon import (
    ensure_ccw,
    locate_point,
    point_in_polygon,
    polygon_area,
    polygon_centroid,
    polygon_orientation,
    polygon_perimeter,
    signed_area,
)


# --- signed_area, polygon_area ------------------------------------------


def test_signed_area_of_a_counter_clockwise_square_is_positive():
    assert signed_area([(0, 0), (4, 0), (4, 4), (0, 4)]) == pytest.approx(16.0, rel=1e-9, abs=1e-9)


def test_signed_area_result_is_a_float():
    assert type(signed_area([(0, 0), (4, 0), (4, 4), (0, 4)])) is float


def test_signed_area_of_points_on_one_line_is_zero():
    assert signed_area([(0, 0), (1, 1), (2, 2)]) == pytest.approx(0.0, rel=1e-9, abs=1e-9)


def test_signed_area_accepts_points_given_as_lists():
    assert signed_area([[0, 0], [2, 0], [0, 2]]) == pytest.approx(2.0, rel=1e-9, abs=1e-9)


def test_signed_area_two_vertices_and_a_closing_vertex_raise_value_error():
    with pytest.raises(ValueError):
        signed_area([(0, 0), (1, 1), (0, 0)])


def test_polygon_area_too_few_vertices_raise_value_error():
    with pytest.raises(ValueError):
        polygon_area([(0, 0)])


# --- polygon_orientation ------------------------------------------------


def test_polygon_orientation_without_area_is_zero():
    assert polygon_orientation([(0, 0), (1, 1), (2, 2)]) == 0


# --- polygon_perimeter --------------------------------------------------


def test_polygon_perimeter_of_a_square():
    result = polygon_perimeter([(0, 0), (4, 0), (4, 4), (0, 4)])
    assert result == pytest.approx(16.0, rel=1e-9, abs=1e-9)


def test_polygon_perimeter_result_is_a_float():
    assert type(polygon_perimeter([(0, 0), (4, 0), (4, 4), (0, 4)])) is float


def test_polygon_perimeter_only_one_closing_vertex_is_dropped():
    polygon = [(0, 0), (3, 4), (0, 0), (0, 0)]
    assert polygon_perimeter(polygon) == pytest.approx(10.0, rel=1e-9, abs=1e-9)


# --- polygon_centroid ---------------------------------------------------


def test_polygon_centroid_of_a_triangle():
    result = polygon_centroid([(0, 0), (6, 0), (0, 3)])
    assert result == pytest.approx((2.0, 1.0), rel=1e-9, abs=1e-9)


def test_polygon_centroid_of_a_shifted_square():
    polygon = [(10, 10), (14, 10), (14, 14), (10, 14)]
    assert polygon_centroid(polygon) == pytest.approx((12.0, 12.0), rel=1e-9, abs=1e-9)


def test_polygon_centroid_of_a_bow_tie_is_the_mean_of_the_vertices():
    polygon = [(0, 0), (2, 2), (2, 0), (0, 2)]
    assert polygon_centroid(polygon) == pytest.approx((1.0, 1.0), rel=1e-9, abs=1e-9)


# --- ensure_ccw ---------------------------------------------------------


def test_ensure_ccw_keeps_a_counter_clockwise_polygon():
    polygon = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert ensure_ccw(polygon) == [(0, 0), (4, 0), (4, 4), (0, 4)]


def test_ensure_ccw_drops_the_closing_vertex():
    polygon = [(0, 0), (0, 2), (2, 0), (0, 0)]
    assert ensure_ccw(polygon) == [(0, 0), (2, 0), (0, 2)]


def test_ensure_ccw_keeps_a_polygon_without_area():
    assert ensure_ccw([(2, 2), (0, 0), (1, 1)]) == [(2, 2), (0, 0), (1, 1)]


def test_ensure_ccw_closing_vertex_given_as_another_type():
    polygon = [[0, 0], [0, 2], [2, 0], (0, 0)]
    assert ensure_ccw(polygon) == [(0, 0), (2, 0), (0, 2)]


# --- locate_point -------------------------------------------------------


def test_locate_point_on_an_edge():
    assert locate_point((4, 1), [(0, 0), (4, 0), (4, 4), (0, 4)]) == "boundary"


def test_locate_point_on_a_horizontal_edge():
    assert locate_point((1, 4), [(0, 0), (4, 0), (4, 4), (0, 4)]) == "boundary"


def test_locate_point_inside_level_with_a_vertex():
    assert locate_point((1, 2), [(2, 0), (4, 2), (2, 4), (0, 2)]) == "inside"


def test_locate_point_on_a_slanted_edge():
    assert locate_point((3, 3), [(2, 0), (4, 2), (2, 4), (0, 2)]) == "boundary"


def test_locate_point_inside_a_concave_polygon():
    polygon = [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)]
    assert locate_point((1, 3), polygon) == "inside"


def test_locate_point_region_covered_once_in_a_self_overlapping_polygon():
    polygon = [(0, 0), (6, 0), (6, 6), (2, 6), (2, 2), (4, 2), (4, 4), (0, 4)]
    assert locate_point((5, 5), polygon) == "inside"


def test_locate_point_close_to_the_left_edge():
    assert locate_point((0.75, 0.5), [(0, 0), (4, 0), (4, 1), (0, 1)]) == "inside"


def test_locate_point_on_a_slanted_edge_with_float_coordinates():
    assert locate_point((0.5, 0.5), [(0, 0), (1, 0), (0, 1)]) == "boundary"


def test_locate_point_too_few_vertices_raise_value_error():
    with pytest.raises(ValueError):
        locate_point((0, 0), [])


# --- point_in_polygon ---------------------------------------------------


def test_point_in_polygon_boundary_counts_by_default():
    assert point_in_polygon((4, 1), [(0, 0), (4, 0), (4, 4), (0, 4)]) is True


def test_point_in_polygon_inside_stays_inside_without_boundary():
    polygon = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert point_in_polygon((2, 2), polygon, include_boundary=False) is True


