import pytest

from toolkit.ledger.account import Account, AccountError, HoldError, InsufficientFunds


# --- construction and properties ----------------------------------------


def test_account_new_account_has_zero_balance_and_no_holds():
    account = Account("Ann")
    assert (account.balance, account.held, account.available) == (0, 0, 0)


def test_account_overdraft_limit_is_available_from_the_start():
    assert Account("Ann", overdraft_limit=100).available == 100


def test_account_error_classes_are_related():
    assert issubclass(AccountError, ValueError)
    assert issubclass(InsufficientFunds, AccountError) and issubclass(HoldError, AccountError)
    account = Account("Ann")
    with pytest.raises(ValueError):
        account.withdraw(1)


# --- deposit ------------------------------------------------------------


def test_account_deposit_zero_raises_account_error():
    with pytest.raises(AccountError):
        Account("Ann").deposit(0)


def test_account_deposit_bool_raises_type_error():
    with pytest.raises(TypeError):
        Account("Ann").deposit(True)


# --- withdraw -----------------------------------------------------------


def test_account_withdraw_returns_the_new_balance():
    account = Account("Ann")
    account.deposit(500)
    assert account.withdraw(120) == 380


def test_account_withdraw_from_empty_account_raises_insufficient_funds():
    with pytest.raises(InsufficientFunds):
        Account("Ann").withdraw(1)


def test_account_withdraw_cannot_use_held_money():
    account = Account("Ann")
    account.deposit(500)
    account.hold(200)
    with pytest.raises(InsufficientFunds):
        account.withdraw(301)
    assert account.withdraw(300) == 200


def test_account_rejected_withdraw_changes_nothing():
    account = Account("Ann", overdraft_limit=10)
    account.deposit(100)
    before = account.statement()
    with pytest.raises(InsufficientFunds):
        account.withdraw(111)
    assert (account.balance, account.available) == (100, 110)
    assert account.statement() == before


# --- hold ---------------------------------------------------------------


def test_account_holds_add_up():
    account = Account("Ann")
    account.deposit(500)
    account.hold(200)
    account.hold(50)
    assert account.held == 250 and account.available == 250


def test_account_rejected_hold_does_not_use_up_an_id():
    account = Account("Ann")
    account.deposit(100)
    with pytest.raises(InsufficientFunds):
        account.hold(500)
    assert account.hold(50) == 1


def test_account_hold_bool_raises_type_error():
    account = Account("Ann")
    account.deposit(100)
    with pytest.raises(TypeError):
        account.hold(True)


# --- release ------------------------------------------------------------


def test_account_release_unknown_id_raises_hold_error():
    account = Account("Ann")
    account.deposit(500)
    with pytest.raises(HoldError):
        account.release(1)


def test_account_rejected_release_changes_nothing():
    account = Account("Ann")
    account.deposit(500)
    account.hold(100)
    before = account.statement()
    with pytest.raises(HoldError):
        account.release(2)
    assert account.held == 100 and account.statement() == before


# --- capture ------------------------------------------------------------


def test_account_capture_part_of_the_hold_frees_the_rest():
    account = Account("Ann")
    account.deposit(500)
    account.hold(200)
    assert account.capture(1, 150) == 350
    assert (account.held, account.available) == (0, 350)


def test_account_capture_zero_raises_account_error():
    account = Account("Ann")
    account.deposit(500)
    account.hold(200)
    with pytest.raises(AccountError):
        account.capture(1, 0)


def test_account_capture_after_release_raises_hold_error():
    account = Account("Ann")
    account.deposit(500)
    account.hold(200)
    account.release(1)
    with pytest.raises(HoldError):
        account.capture(1)


def test_account_rejected_capture_keeps_the_hold_active():
    account = Account("Ann")
    account.deposit(500)
    account.hold(200)
    before = account.statement()
    with pytest.raises(AccountError):
        account.capture(1, 500)
    assert (account.balance, account.held) == (500, 200)
    assert account.statement() == before
    assert account.capture(1) == 300


# --- statement ----------------------------------------------------------


def test_account_statement_deposit_line():
    account = Account("Ann")
    account.deposit(500)
    assert account.statement().split("\n")[1] == "1 deposit +500 500"


def test_account_statement_hold_and_release_lines():
    account = Account("Ann")
    account.deposit(500)
    account.hold(200, "hotel")
    account.release(1)
    lines = account.statement().split("\n")
    assert lines[2] == "2 hold#1 (200) 500 hotel"
    assert lines[3] == "3 release#1 (200) 500 hotel"


def test_account_statement_negative_balance():
    account = Account("Ann", overdraft_limit=100)
    account.withdraw(30)
    lines = account.statement().split("\n")
    assert lines[1] == "1 withdraw -30 -30"
    assert lines[2] == "Balance: -30, held: 0, available: 70"


def test_account_statement_skips_rejected_operations():
    account = Account("Ann")
    account.deposit(100)
    with pytest.raises(InsufficientFunds):
        account.withdraw(500)
    with pytest.raises(HoldError):
        account.release(9)
    account.withdraw(40)
    assert account.statement() == (
        "Account: Ann\n"
        "1 deposit +100 100\n"
        "2 withdraw -40 60\n"
        "Balance: 60, held: 0, available: 60"
    )


