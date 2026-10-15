import pytest

from toolkit.calc.expr import ExprError, ExprNameError, ExprSyntaxError, evaluate


# --- numbers and binary operators ---------------------------------------


def test_evaluate_single_number():
    assert evaluate("42") == pytest.approx(42.0, rel=1e-9, abs=1e-9)


def test_evaluate_multiplication_before_addition():
    assert evaluate("2 + 3 * 4") == pytest.approx(14.0, rel=1e-9, abs=1e-9)


def test_evaluate_nested_parentheses():
    assert evaluate("((1 + 2) * (3 + 4)) / 7") == pytest.approx(3.0, rel=1e-9, abs=1e-9)


def test_evaluate_division_is_true_division():
    assert evaluate("7 / 2") == pytest.approx(3.5, rel=1e-9, abs=1e-9)


def test_evaluate_modulo_with_negative_right_operand():
    assert evaluate("7 % -3") == pytest.approx(-2.0, rel=1e-9, abs=1e-9)


def test_evaluate_ignores_whitespace():
    assert evaluate(" \t1+\n2 * 3 ") == pytest.approx(7.0, rel=1e-9, abs=1e-9)


# --- power and unary operators ------------------------------------------


def test_evaluate_power_is_right_associative():
    assert evaluate("2 ^ 3 ^ 2") == pytest.approx(512.0, rel=1e-9, abs=1e-9)


def test_evaluate_parenthesised_negative_base():
    assert evaluate("(-3) ^ 2") == pytest.approx(9.0, rel=1e-9, abs=1e-9)


def test_evaluate_fractional_exponent():
    assert evaluate("9 ^ 0.5") == pytest.approx(3.0, rel=1e-9, abs=1e-9)


def test_evaluate_repeated_unary_operators():
    assert evaluate("-+-5") == pytest.approx(5.0, rel=1e-9, abs=1e-9)


def test_evaluate_unary_minus_before_parentheses():
    assert evaluate("-(2 + 3)") == pytest.approx(-5.0, rel=1e-9, abs=1e-9)


# --- variables and constants --------------------------------------------


def test_evaluate_int_variable_gives_float_result():
    result = evaluate("n", {"n": 3})
    assert type(result) is float and result == 3.0


def test_evaluate_constant_e():
    assert evaluate("e") == pytest.approx(2.718281828459045, rel=1e-9, abs=1e-9)


def test_evaluate_unknown_variable_next_to_known_one_raises_name_error():
    with pytest.raises(ExprNameError):
        evaluate("x + y", {"x": 1})


# --- functions ----------------------------------------------------------


def test_evaluate_abs():
    assert evaluate("abs(-3.5)") == pytest.approx(3.5, rel=1e-9, abs=1e-9)


def test_evaluate_ceil():
    assert evaluate("ceil(2.1)") == pytest.approx(3.0, rel=1e-9, abs=1e-9)


def test_evaluate_min_with_several_arguments():
    assert evaluate("min(3, 1, 2)") == pytest.approx(1.0, rel=1e-9, abs=1e-9)


def test_evaluate_max_with_one_argument():
    assert evaluate("max(7)") == pytest.approx(7.0, rel=1e-9, abs=1e-9)


def test_evaluate_function_call_as_power_base():
    assert evaluate("sqrt(16) ^ 2") == pytest.approx(16.0, rel=1e-9, abs=1e-9)


def test_evaluate_variable_may_share_name_with_function():
    result = evaluate("min + max(1, 2)", {"min": 10})
    assert result == pytest.approx(12.0, rel=1e-9, abs=1e-9)


def test_evaluate_too_many_arguments_raises_expr_error():
    with pytest.raises(ExprError):
        evaluate("sqrt(1, 2)")


def test_evaluate_two_arguments_for_ceil_raise_expr_error():
    with pytest.raises(ExprError):
        evaluate("ceil(1, 2)")


def test_evaluate_sqrt_of_negative_number_raises_expr_error():
    with pytest.raises(ExprError):
        evaluate("sqrt(0 - 4)")


# --- arithmetic errors --------------------------------------------------


def test_evaluate_modulo_by_zero_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError):
        evaluate("5 % 0")


def test_evaluate_power_too_large_for_float_raises_expr_error():
    with pytest.raises(ExprError):
        evaluate("10 ^ 1000")


# --- syntax errors ------------------------------------------------------


def test_evaluate_missing_right_operand_raises_syntax_error():
    with pytest.raises(ExprSyntaxError):
        evaluate("1 +")


def test_evaluate_surplus_closing_parenthesis_raises_syntax_error():
    with pytest.raises(ExprSyntaxError):
        evaluate("1 + 2)")


def test_evaluate_number_followed_by_name_raises_syntax_error():
    with pytest.raises(ExprSyntaxError):
        evaluate("2 x", {"x": 3})


def test_evaluate_lone_dot_raises_syntax_error():
    with pytest.raises(ExprSyntaxError):
        evaluate("1 + .")


def test_evaluate_operator_instead_of_opening_parenthesis_raises_syntax_error():
    with pytest.raises(ExprSyntaxError):
        evaluate("2 + * 3)")


def test_evaluate_unclosed_call_raises_syntax_error():
    with pytest.raises(ExprSyntaxError):
        evaluate("max(1, 2")


# --- exception hierarchy ------------------------------------------------


def test_evaluate_syntax_error_is_an_expr_error():
    with pytest.raises(ExprError):
        evaluate("1 +")


