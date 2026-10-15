import pytest

from toolkit.ledger.change import ChangeError, count_ways, fewest_pieces, make_change


# --- make_change --------------------------------------------------------


def test_make_change_single_piece():
    assert make_change(5, {5: 1}) == {5: 1}


def test_make_change_amount_zero_gives_empty_dict():
    assert make_change(0, {5: 3}) == {}


def test_make_change_finds_a_solution_where_largest_first_gets_stuck():
    assert make_change(6, {5: 1, 2: 3}) == {2: 3}


def test_make_change_limited_stock_forces_smaller_pieces():
    assert make_change(40, {25: 1, 10: 1, 5: 1, 1: 10}) == {25: 1, 10: 1, 5: 1}
    assert make_change(41, {25: 1, 10: 1, 1: 10}) == {25: 1, 10: 1, 1: 6}


def test_make_change_unused_denominations_are_left_out():
    result = make_change(20, {20: 1, 10: 5, 1: 5})
    assert result == {20: 1} and list(result) == [20]


def test_make_change_tie_break_does_not_depend_on_dict_order():
    assert make_change(10, {3: 1, 5: 2, 7: 1}) == {7: 1, 3: 1}


def test_make_change_number_of_pieces_matters_more_than_the_tie_break():
    assert make_change(12, {9: 1, 6: 2, 2: 1, 1: 1}) == {6: 2}


def test_make_change_empty_stock_raises_change_error():
    with pytest.raises(ChangeError):
        make_change(1, {})


def test_make_change_zero_denomination_raises_change_error():
    with pytest.raises(ChangeError):
        make_change(5, {0: 1, 5: 1})


def test_make_change_invalid_stock_raises_even_for_amount_zero():
    with pytest.raises(ChangeError):
        make_change(0, {5: -1})


def test_make_change_by_keyword_arguments():
    assert make_change(amount=8, stock={5: 1, 4: 2, 1: 3}) == {4: 2}


# --- fewest_pieces ------------------------------------------------------


def test_fewest_pieces_result_is_an_int():
    result = fewest_pieces(63, {1: 3, 10: 1, 25: 2, 5: 1})
    assert result == 6 and type(result) is int


def test_fewest_pieces_empty_stock_gives_none():
    assert fewest_pieces(1, {}) is None


def test_fewest_pieces_negative_amount_raises_change_error():
    with pytest.raises(ChangeError):
        fewest_pieces(-1, {1: 5})


# --- count_ways ---------------------------------------------------------


def test_count_ways_result_is_an_int():
    assert type(count_ways(5, [1, 2, 5])) is int


def test_count_ways_does_not_depend_on_the_order_of_denominations():
    assert count_ways(11, [5, 2, 1]) == count_ways(11, [1, 2, 5]) == 11


def test_count_ways_amount_zero_has_one_way():
    assert count_ways(0, [1, 2]) == 1


def test_count_ways_single_denomination():
    assert count_ways(10, [5]) == 1 and count_ways(10, [10]) == 1 and count_ways(10, [20]) == 0


def test_count_ways_dict_with_enough_pieces_equals_unlimited():
    assert count_ways(5, {1: 5, 2: 5, 5: 5}) == 4


def test_count_ways_dict_where_the_amount_cannot_be_made():
    assert count_ways(11, {5: 3, 2: 0}) == 0


def test_count_ways_negative_denomination_raises_change_error():
    with pytest.raises(ChangeError):
        count_ways(5, [1, -2])


