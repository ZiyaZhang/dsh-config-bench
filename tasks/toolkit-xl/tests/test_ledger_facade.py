import pytest

import toolkit.ledger
from toolkit.ledger.account import Account, AccountError, HoldError, InsufficientFunds
from toolkit.ledger.change import ChangeError
from toolkit.ledger.inventory import Inventory, StockError
from toolkit.ledger.money import MoneyError


# --- change_due ---------------------------------------------------------


def test_change_due_lists_one_text_per_piece():
    stock = {200: 1, 100: 1, 50: 2, 20: 1, 10: 2, 5: 1}
    assert toolkit.ledger.change_due("7.35 EUR", "10 EUR", stock) == [
        "2.00 EUR",
        "0.50 EUR",
        "0.10 EUR",
        "0.05 EUR",
    ]


def test_change_due_uses_the_fewest_pieces_not_the_largest_first():
    stock = {4: 1, 3: 2, 1: 2}
    assert toolkit.ledger.change_due("0.94 USD", "1 USD", stock) == ["0.03 USD", "0.03 USD"]


def test_change_due_exact_payment_gives_empty_list():
    assert toolkit.ledger.change_due("4.00 USD", "4 USD", {}) == []


def test_change_due_result_is_a_list_of_strings():
    result = toolkit.ledger.change_due("1 USD", "2 USD", {100: 1})
    assert type(result) is list and type(result[0]) is str


def test_change_due_unparsable_price_raises_money_error():
    with pytest.raises(MoneyError):
        toolkit.ledger.change_due("five", "10 EUR", {500: 1})


def test_change_due_does_not_modify_the_stock():
    stock = {100: 2, 50: 1}
    toolkit.ledger.change_due("0.50 USD", "2 USD", stock)
    assert stock == {100: 2, 50: 1}


# --- re-exports ---------------------------------------------------------


def test_ledger_facade_exposes_account():
    account = toolkit.ledger.Account("Ann")
    assert account.deposit(10) == 10
    assert toolkit.ledger.Account is Account


def test_ledger_facade_error_classes_are_the_classes_of_the_modules():
    with pytest.raises(MoneyError):
        toolkit.ledger.parse_money("nothing")
    with pytest.raises(ChangeError):
        toolkit.ledger.make_change(1, {})
    assert toolkit.ledger.MoneyError is MoneyError
    assert toolkit.ledger.ChangeError is ChangeError
    assert toolkit.ledger.StockError is StockError
    assert toolkit.ledger.AccountError is AccountError
    assert toolkit.ledger.InsufficientFunds is InsufficientFunds
    assert toolkit.ledger.HoldError is HoldError


