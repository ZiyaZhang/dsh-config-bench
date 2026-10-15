import pytest

from toolkit.ledger.inventory import Inventory, StockError


# --- receive, on_hand, layers -------------------------------------------


def test_inventory_new_inventory_is_empty():
    inventory = Inventory()
    assert inventory.skus() == [] and inventory.valuation() == 0


def test_inventory_receive_does_not_merge_layers_of_equal_cost():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.receive("nut", 4, 5)
    assert inventory.layers("nut") == [(10, 5), (4, 5)]


def test_inventory_receive_negative_quantity_raises_stock_error():
    with pytest.raises(StockError):
        Inventory().receive("nut", -3, 5)


def test_inventory_stock_error_is_a_value_error():
    with pytest.raises(ValueError):
        Inventory().receive("nut", 0, 5)
    assert issubclass(StockError, ValueError)


def test_inventory_skus_are_kept_apart():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.receive("bolt", 4, 20)
    assert inventory.layers("nut") == [(10, 5)] and inventory.layers("bolt") == [(4, 20)]


# --- issue --------------------------------------------------------------


def test_inventory_issue_result_is_a_tuple_of_ints():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    result = inventory.issue("nut", 4)
    assert type(result) is tuple and type(result[0]) is int and type(result[1]) is int


def test_inventory_issue_exactly_one_layer_removes_it():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.receive("nut", 10, 7)
    assert inventory.issue("nut", 10) == (10, 50)
    assert inventory.layers("nut") == [(10, 7)]


def test_inventory_issue_uses_newer_costs_only_after_older_layers():
    inventory = Inventory()
    inventory.receive("nut", 1, 100)
    inventory.receive("nut", 1, 1)
    assert inventory.issue("nut", 1) == (1, 100)
    assert inventory.issue("nut", 1) == (1, 1)


def test_inventory_rejected_issue_takes_nothing():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.receive("nut", 10, 7)
    with pytest.raises(StockError):
        inventory.issue("nut", 21)
    assert inventory.layers("nut") == [(10, 5), (10, 7)] and inventory.returnable("nut") == 0


def test_inventory_issue_only_touches_its_sku():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.receive("bolt", 4, 20)
    inventory.issue("bolt", 3)
    assert inventory.layers("nut") == [(10, 5)] and inventory.layers("bolt") == [(1, 20)]


# --- issue with partial -------------------------------------------------


def test_inventory_partial_issue_of_unknown_sku_gives_zero():
    inventory = Inventory()
    assert inventory.issue("gear", 5, partial=True) == (0, 0)
    assert inventory.skus() == [] and inventory.returnable("gear") == 0


# --- return_units -------------------------------------------------------


def test_inventory_return_units_joins_the_oldest_layer_of_equal_cost():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.issue("nut", 4)
    inventory.return_units("nut", 3)
    assert inventory.layers("nut") == [(9, 5)]


def test_inventory_return_units_across_issue_pieces():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.receive("nut", 10, 7)
    inventory.issue("nut", 15)
    assert inventory.return_units("nut", 8) == 50
    assert inventory.layers("nut") == [(3, 5), (10, 7)]


def test_inventory_return_units_into_empty_stock():
    inventory = Inventory()
    inventory.receive("nut", 3, 5)
    inventory.issue("nut", 3)
    assert inventory.return_units("nut", 2) == 10
    assert inventory.layers("nut") == [(2, 5)] and inventory.skus() == ["nut"]


def test_inventory_returned_units_are_issued_first_again():
    inventory = Inventory()
    inventory.receive("nut", 2, 5)
    inventory.receive("nut", 2, 7)
    inventory.issue("nut", 3)
    inventory.return_units("nut", 2)
    assert inventory.layers("nut") == [(1, 5), (2, 7)]
    assert inventory.issue("nut", 2) == (2, 12)


def test_inventory_return_units_of_unknown_sku_raises_stock_error():
    with pytest.raises(StockError):
        Inventory().return_units("gear", 1)


def test_inventory_units_cannot_be_returned_twice():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.issue("nut", 4)
    inventory.return_units("nut", 4)
    with pytest.raises(StockError):
        inventory.return_units("nut", 1)


# --- returnable ---------------------------------------------------------


def test_inventory_returnable_counts_partial_issues():
    inventory = Inventory()
    inventory.receive("nut", 3, 5)
    inventory.issue("nut", 10, partial=True)
    assert inventory.returnable("nut") == 3


# --- valuation ----------------------------------------------------------


def test_inventory_valuation_of_all_skus():
    inventory = Inventory()
    inventory.receive("nut", 10, 5)
    inventory.receive("bolt", 4, 20)
    assert inventory.valuation() == 130 and inventory.valuation(sku=None) == 130


def test_inventory_valuation_result_is_an_int():
    inventory = Inventory()
    assert type(inventory.valuation()) is int and type(inventory.valuation("x")) is int


# --- skus ---------------------------------------------------------------


def test_inventory_skus_keep_their_place_when_stock_comes_back():
    inventory = Inventory()
    inventory.receive("nut", 1, 1)
    inventory.receive("bolt", 1, 1)
    inventory.issue("nut", 1)
    inventory.receive("nut", 5, 2)
    assert inventory.skus() == ["nut", "bolt"]


