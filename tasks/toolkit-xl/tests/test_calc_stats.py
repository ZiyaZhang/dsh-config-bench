import pytest

from toolkit.calc.stats import mean, median, mode, percentile, stdev, variance


# --- mean ---------------------------------------------------------------


def test_mean_of_integers():
    assert mean([1, 2, 3, 4]) == pytest.approx(2.5, rel=1e-9, abs=1e-9)


def test_mean_with_negative_and_float_values():
    assert mean([-1.5, 2.5, 5]) == pytest.approx(2.0, rel=1e-9, abs=1e-9)


def test_mean_empty_raises_value_error():
    with pytest.raises(ValueError):
        mean([])


# --- median -------------------------------------------------------------


def test_median_odd_count_is_middle_value():
    assert median([5, 1, 3]) == pytest.approx(3.0, rel=1e-9, abs=1e-9)


def test_median_of_single_value():
    assert median([9]) == pytest.approx(9.0, rel=1e-9, abs=1e-9)


def test_median_empty_raises_value_error():
    with pytest.raises(ValueError):
        median([])


# --- mode ---------------------------------------------------------------


def test_mode_tie_gives_smallest_value():
    assert mode([5, 5, 2, 2, 9]) == 2


def test_mode_of_floats():
    assert mode([1.5, 2.5, 1.5]) == 1.5


def test_mode_non_number_raises_type_error():
    with pytest.raises(TypeError):
        mode(["a", "a", "b"])


# --- percentile ---------------------------------------------------------


def test_percentile_fifty_is_median_for_even_count():
    assert percentile([4, 1, 3, 2], 50) == pytest.approx(2.5, rel=1e-9, abs=1e-9)


def test_percentile_sorts_the_values_first():
    assert percentile([50, 10, 40, 20, 30], 25) == pytest.approx(20.0, rel=1e-9, abs=1e-9)


def test_percentile_uneven_spacing():
    assert percentile([1, 2, 10, 100], 90) == pytest.approx(73.0, rel=1e-9, abs=1e-9)


def test_percentile_above_hundred_raises_value_error():
    with pytest.raises(ValueError):
        percentile([1, 2, 3], 100.5)


# --- variance and stdev -------------------------------------------------


def test_variance_sample():
    result = variance([2, 4, 4, 4, 5, 5, 7, 9], sample=True)
    assert result == pytest.approx(32 / 7, rel=1e-9, abs=1e-9)


def test_variance_sample_of_single_value_raises_value_error():
    with pytest.raises(ValueError):
        variance([5], sample=True)


def test_stdev_sample():
    result = stdev([1, 2, 3, 4], sample=True)
    assert result == pytest.approx(1.2909944487358056, rel=1e-9, abs=1e-9)


def test_stdev_bool_element_raises_type_error():
    with pytest.raises(TypeError):
        stdev([1, False])
