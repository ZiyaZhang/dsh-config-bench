import pytest

from toolkit.geom.vec import (
    almost_equal,
    angle_between,
    angle_of,
    compare_points,
    cross,
    distance,
    dot,
    norm,
    rotate,
    round_vec,
    unit_vector,
    vec_add,
    vec_scale,
    vec_sub,
)


# --- vec_add, vec_sub, vec_scale ----------------------------------------


def test_vec_add_adds_coordinates():
    assert vec_add((1, 2), (3, 4)) == (4, 6)


def test_vec_sub_subtracts_the_second_vector():
    assert vec_sub((1, 2), (3, 4.5)) == (-2, -2.5)


def test_vec_scale_by_a_float():
    assert vec_scale([1, 2], 0.5) == (0.5, 1.0)


# --- dot, cross ---------------------------------------------------------


def test_dot_of_perpendicular_vectors_is_zero():
    assert dot((2, 3), (-3, 2)) == 0


def test_cross_is_positive_for_a_counter_clockwise_turn():
    assert cross((1, 0), (0, 1)) == 1


# --- norm, distance, unit_vector ----------------------------------------


def test_norm_of_three_four_is_five():
    assert norm((3, 4)) == pytest.approx(5.0, rel=1e-9, abs=1e-9)


def test_norm_ignores_the_signs():
    assert norm((-6, -8)) == pytest.approx(10.0, rel=1e-9, abs=1e-9)


def test_distance_does_not_depend_on_the_order():
    assert distance((4, 5), (1, 1)) == pytest.approx(distance((1, 1), (4, 5)), rel=1e-9, abs=1e-9)


def test_unit_vector_of_the_zero_vector_raises_value_error():
    with pytest.raises(ValueError):
        unit_vector((0, 0))


# --- round_vec ----------------------------------------------------------


def test_round_vec_negative_half_goes_up_too():
    assert round_vec((-2.5, -0.5)) == (-2.0, 0.0)


def test_round_vec_negative_ordinary_values():
    assert round_vec((-2.4, -2.6)) == (-2.0, -3.0)


def test_round_vec_one_digit_tie_goes_up():
    assert round_vec((1.25, -1.25), 1) == pytest.approx((1.3, -1.2), rel=1e-9, abs=1e-9)


# --- angle_of, angle_between --------------------------------------------


def test_angle_of_positive_x_axis_is_zero():
    assert angle_of((1, 0)) == pytest.approx(0.0, rel=1e-9, abs=1e-9)


def test_angle_of_negative_y_axis_is_270():
    assert angle_of((0, -1)) == pytest.approx(270.0, rel=1e-9, abs=1e-9)


def test_angle_of_third_quadrant_is_225():
    assert angle_of((-1, -1)) == pytest.approx(225.0, rel=1e-9, abs=1e-9)


def test_angle_of_the_zero_vector_raises_value_error():
    with pytest.raises(ValueError):
        angle_of((0, 0))


def test_angle_between_parallel_vectors_is_zero():
    assert angle_between((0, 3), (0, 1)) == pytest.approx(0.0, rel=1e-9, abs=1e-9)


def test_angle_between_obtuse_angle():
    assert angle_between((1, 0), (-1, 1)) == pytest.approx(135.0, rel=1e-9, abs=1e-9)


# --- rotate -------------------------------------------------------------


def test_rotate_quarter_turn_is_exact():
    assert rotate((1, 0), 90) == (0, 1)


def test_rotate_three_quarter_turn_is_exact():
    assert rotate((1, 0), 270) == (0, -1)


def test_rotate_more_than_a_full_turn():
    assert rotate((1, 2), 450) == (-2, 1)


def test_rotate_float_multiple_of_90_is_exact():
    assert rotate((1, 0), 90.0) == (0, 1)


def test_rotate_three_quarter_turn_about_a_center_in_general_position():
    assert rotate((5, 7), 270, (2, 3)) == (6, 0)


def test_rotate_by_30_degrees():
    assert rotate((1, 0), 30) == pytest.approx((0.8660254037844387, 0.5), rel=1e-9, abs=1e-9)


def test_rotate_point_in_general_position_by_30_degrees():
    expected = (0.598076211353316, 4.964101615137754)
    assert rotate((3, 4), 30) == pytest.approx(expected, rel=1e-9, abs=1e-9)


# --- almost_equal -------------------------------------------------------


def test_almost_equal_same_point():
    assert almost_equal((1, 2), (1.0, 2.0)) is True


def test_almost_equal_difference_of_exactly_tol_counts_as_equal():
    assert almost_equal((0, 0), (0.5, -0.5), 0.5) is True


def test_almost_equal_with_tolerance_zero():
    assert almost_equal((1, 2), (1, 2), 0) is True and almost_equal((1, 2), (1, 2.5), 0) is False


# --- compare_points -----------------------------------------------------


def test_compare_points_larger_x_comes_last():
    assert compare_points((2, 0), (1, 9)) == 1


def test_compare_points_x_within_tolerance_is_decided_by_y():
    assert compare_points((1, 5), (1.0000000001, 2)) == 1


def test_compare_points_with_a_large_tolerance():
    assert compare_points((0, 0), (0.4, 1), tol=0.5) == -1


def test_compare_points_negative_tolerance_raises_value_error():
    with pytest.raises(ValueError):
        compare_points((0, 0), (0, 0), -0.5)
