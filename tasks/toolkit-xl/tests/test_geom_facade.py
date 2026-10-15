import pytest

import toolkit.geom
from toolkit.geom.hull import convex_hull
from toolkit.geom.polygon import locate_point
from toolkit.geom.segment import point_on_segment


# --- locate_in_hull -----------------------------------------------------


def test_locate_in_hull_point_inside_a_triangle():
    assert toolkit.geom.locate_in_hull((1, 1), [(0, 0), (4, 0), (0, 4)]) == "inside"


def test_locate_in_hull_point_outside():
    assert toolkit.geom.locate_in_hull((3, 3), [(0, 0), (4, 0), (0, 4)]) == "outside"


def test_locate_in_hull_point_on_the_edge_that_closes_a_notch():
    points = [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)]
    assert toolkit.geom.locate_in_hull((3, 3), points) == "boundary"


def test_locate_in_hull_points_on_one_line_point_between_them():
    assert toolkit.geom.locate_in_hull((1, 1), [(0, 0), (2, 2), (3, 3)]) == "boundary"


def test_locate_in_hull_single_point_is_its_own_boundary():
    assert toolkit.geom.locate_in_hull((5, 5), [(5, 5), (5, 5)]) == "boundary"


# --- re-exports ---------------------------------------------------------


def test_geom_facade_exposes_vec_functions():
    assert toolkit.geom.vec_add((1, 2), (3, 4)) == (4, 6)
    assert toolkit.geom.vec_sub((1, 2), (3, 4)) == (-2, -2)
    assert toolkit.geom.vec_scale((1, 2), 2) == (2, 4)
    assert toolkit.geom.dot((1, 2), (3, 4)) == 11
    assert toolkit.geom.cross((1, 2), (3, 4)) == -2
    assert toolkit.geom.norm((3, 4)) == pytest.approx(5.0, rel=1e-9, abs=1e-9)
    assert toolkit.geom.distance((0, 0), (3, 4)) == pytest.approx(5.0, rel=1e-9, abs=1e-9)
    assert toolkit.geom.unit_vector((0, 2)) == pytest.approx((0.0, 1.0), rel=1e-9, abs=1e-9)
    assert toolkit.geom.round_vec((0.5, 1.5)) == (1.0, 2.0)
    assert toolkit.geom.angle_of((0, 1)) == pytest.approx(90.0, rel=1e-9, abs=1e-9)
    assert toolkit.geom.angle_between((1, 0), (0, 1)) == pytest.approx(90.0, rel=1e-9, abs=1e-9)
    assert toolkit.geom.rotate((1, 0), 90) == (0, 1)
    assert toolkit.geom.almost_equal((0, 0), (0, 0)) is True
    assert toolkit.geom.compare_points((0, 0), (1, 0)) == -1


def test_geom_facade_exposes_hull_functions():
    points = [(0, 0), (2, 0), (2, 2), (0, 2), (1, 1)]
    assert toolkit.geom.convex_hull(points) == [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert toolkit.geom.bounding_box(points) == ((0, 0), (2, 2))
    assert toolkit.geom.farthest_pair(points) == ((0, 0), (2, 2))
    assert toolkit.geom.diameter([(0, 0), (3, 4)]) == pytest.approx(5.0, rel=1e-9, abs=1e-9)


