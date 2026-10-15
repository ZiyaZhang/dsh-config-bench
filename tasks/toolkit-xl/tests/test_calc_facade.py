import pytest

import toolkit.calc
from toolkit.calc.expr import ExprError, ExprNameError, ExprSyntaxError
from toolkit.calc.units import UnitError


# --- stat_expr ----------------------------------------------------------


def test_stat_expr_mean():
    result = toolkit.calc.stat_expr("mean", [1, 2, 3, 4])
    assert result == pytest.approx(2.5, rel=1e-9, abs=1e-9)


def test_stat_expr_n_and_total():
    result = toolkit.calc.stat_expr("n * 100 + total", [3, 5, 10])
    assert result == pytest.approx(318.0, rel=1e-9, abs=1e-9)


def test_stat_expr_functions_and_constants_are_available():
    result = toolkit.calc.stat_expr("sqrt(n) + floor(pi)", [1, 2, 3, 4])
    assert result == pytest.approx(5.0, rel=1e-9, abs=1e-9)


def test_stat_expr_empty_values_raise_value_error():
    with pytest.raises(ValueError):
        toolkit.calc.stat_expr("mean", [])


def test_stat_expr_malformed_expression_raises_syntax_error():
    with pytest.raises(ExprSyntaxError):
        toolkit.calc.stat_expr("mean +", [1, 2])


# --- re-exports ---------------------------------------------------------


def test_facade_exposes_interval_functions():
    assert toolkit.calc.merge_intervals([(1, 2), (3, 4)]) == [(1, 4)]
    assert toolkit.calc.intersect_intervals([(1, 5)], [(4, 9)]) == [(4, 5)]
    assert toolkit.calc.subtract_intervals([(1, 5)], [(4, 9)]) == [(1, 3)]
    assert toolkit.calc.count_points([(1, 5)]) == 5


def test_calc_facade_error_classes_are_the_classes_of_the_modules():
    with pytest.raises(UnitError):
        toolkit.calc.convert(1, "kg", "m")
    assert toolkit.calc.UnitError is UnitError
    assert toolkit.calc.ExprError is ExprError
    assert toolkit.calc.ExprSyntaxError is ExprSyntaxError
    assert toolkit.calc.ExprNameError is ExprNameError
