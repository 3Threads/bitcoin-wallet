import os
from uuid import uuid4

import pytest

from core.errors import (
    InvalidApiKeyError,
    NotEnoughBitcoinError,
    TransactionBetweenSameWalletError,
    WalletDoesNotExistError,
    WalletPermissionError,
)
from core.user import generate_api_key
from infra.constants import MINIMUM_AMOUNT_OF_BITCOIN, SQL_FILE_TEST
from infra.sqlite.database_connect import Database
from infra.sqlite.transactions import TransactionsDataBase
from infra.sqlite.users import UsersDatabase
from infra.sqlite.wallets import WalletsDatabase


@pytest.fixture
def db() -> Database:
    db = Database(":memory:", os.path.abspath(SQL_FILE_TEST))
    db.initial()
    return db


def test_make_transaction(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create("test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    from_wallet = wallets.create(user.api_key)
    to_wallet = wallets.create(user.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    transaction = transactions.make_transaction(
        user.api_key, from_wallet.address, to_wallet.address, 0.5
    )
    from_wallet = wallets.read(from_wallet.address, user.api_key, False)
    to_wallet = wallets.read(to_wallet.address, user.api_key, False)
    assert transaction.from_address == from_wallet.address
    assert transaction.to_address == to_wallet.address
    assert transaction.transaction_amount == 0.5
    assert transaction.transaction_fee == 0

    assert from_wallet.get_balance() == 0.5
    assert to_wallet.get_balance() == 1.5
    db.close_database()


def test_make_transaction_between_two_users(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    from_wallet = wallets.create(user1.api_key)
    to_wallet = wallets.create(user2.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    transaction = transactions.make_transaction(
        user1.api_key, from_wallet.address, to_wallet.address, 1
    )
    from_wallet = wallets.read(from_wallet.address, user1.api_key, False)
    to_wallet = wallets.read(to_wallet.address, user2.api_key, False)
    assert transaction.from_address == from_wallet.address
    assert transaction.to_address == to_wallet.address
    assert transaction.transaction_amount == 1
    assert transaction.transaction_fee == 0.015
    assert from_wallet.get_balance() == 0
    assert to_wallet.get_balance() == 1.985
    db.close_database()


def test_transaction_less_then_one_satoshi(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    from_wallet = wallets.create(user1.api_key)
    to_wallet = wallets.create(user2.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    transaction = transactions.make_transaction(
        user1.api_key,
        from_wallet.address,
        to_wallet.address,
        0.5 * MINIMUM_AMOUNT_OF_BITCOIN,
    )
    from_wallet = wallets.read(from_wallet.address, user1.api_key, False)
    to_wallet = wallets.read(to_wallet.address, user2.api_key, False)
    assert transaction.from_address == from_wallet.address
    assert transaction.to_address == to_wallet.address
    assert from_wallet.get_balance() == 1 - MINIMUM_AMOUNT_OF_BITCOIN
    assert to_wallet.get_balance() == 1


def test_double_transaction_with_less_then_one_satoshi_fee(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    from_wallet = wallets.create(user1.api_key)
    to_wallet = wallets.create(user2.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    transaction = transactions.make_transaction(
        user1.api_key,
        from_wallet.address,
        to_wallet.address,
        1 - 2 * MINIMUM_AMOUNT_OF_BITCOIN,
    )
    from_wallet = wallets.read(from_wallet.address, user1.api_key, False)
    to_wallet = wallets.read(to_wallet.address, user2.api_key, False)
    assert transaction.from_address == from_wallet.address
    assert transaction.to_address == to_wallet.address
    from_wallet = wallets.read(from_wallet.address, user1.api_key, False)
    to_wallet = wallets.read(to_wallet.address, user2.api_key, False)
    assert from_wallet.get_balance() == 2 * MINIMUM_AMOUNT_OF_BITCOIN
    assert to_wallet.get_balance() == 1.98499998

    transaction2 = transactions.make_transaction(
        user1.api_key,
        from_wallet.address,
        to_wallet.address,
        1.5 * MINIMUM_AMOUNT_OF_BITCOIN,
    )
    from_wallet = wallets.read(from_wallet.address, user1.api_key, False)
    to_wallet = wallets.read(to_wallet.address, user2.api_key, False)

    assert transaction2.from_address == from_wallet.address
    assert transaction2.to_address == to_wallet.address
    assert to_wallet.get_balance() == 1.98499999
    assert from_wallet.get_balance() == 0


def test_make_transaction_without_enough_balance(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create("test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    from_wallet = wallets.create(user.api_key)
    to_wallet = wallets.create(user.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    with pytest.raises(NotEnoughBitcoinError):
        transactions.make_transaction(
            user.api_key, from_wallet.address, to_wallet.address, 1.5
        )
    db.close_database()


def test_make_transaction_between_same_wallet(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create("test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    wallet = wallets.create(user.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    with pytest.raises(TransactionBetweenSameWalletError):
        transactions.make_transaction(user.api_key, wallet.address, wallet.address, 0.5)
    db.close_database()


def test_make_transaction_other_api_key(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )

    with pytest.raises(WalletPermissionError):
        transactions.make_transaction(
            user2.api_key,
            wallets.create(user1.api_key).address,
            wallets.create(user2.api_key).address,
            0.5,
        )
    db.close_database()


def test_make_transaction_unknown_wallet_address(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )

    with pytest.raises(WalletDoesNotExistError):
        transactions.make_transaction(
            users.create("test@gmail.com").api_key, uuid4(), uuid4(), 0.5
        )
    db.close_database()


def test_make_transaction_unknown_api_key(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )

    with pytest.raises(InvalidApiKeyError):
        transactions.make_transaction(generate_api_key(), uuid4(), uuid4(), 0.5)
    db.close_database()


def test_read_all_transactions_empty(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create("test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )

    assert transactions.read_all(user.api_key) == []
    db.close_database()


def test_read_all_transactions(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    wallet1 = wallets.create(user1.api_key)
    wallet2 = wallets.create(user2.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    transaction1 = transactions.make_transaction(
        user1.api_key, wallet1.address, wallet2.address, 0.5
    )
    transaction2 = transactions.make_transaction(
        user2.api_key, wallet2.address, wallet1.address, 0.5
    )
    assert transactions.read_all(user1.api_key) == [transaction1, transaction2]
    db.close_database()


def test_read_all_transactions_unknown_api_key(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )

    with pytest.raises(InvalidApiKeyError):
        transactions.read_all(generate_api_key())
    db.close_database()


def test_get_wallet_transactions_unknown_api_key(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )

    with pytest.raises(InvalidApiKeyError):
        transactions.get_wallet_transactions(generate_api_key(), uuid4())
    db.close_database()


def test_get_wallet_transactions_unknown_wallet_address(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )

    with pytest.raises(WalletDoesNotExistError):
        transactions.get_wallet_transactions(
            users.create("test@gmail.com").api_key, uuid4()
        )
    db.close_database()


def test_get_wallet_transactions_other_api_key(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )

    with pytest.raises(WalletPermissionError):
        transactions.get_wallet_transactions(
            user2.api_key, wallets.create(user1.api_key).address
        )
    db.close_database()


def test_get_wallet_transactions(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    wallet1 = wallets.create(user1.api_key)
    wallet2 = wallets.create(user2.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    transaction1 = transactions.make_transaction(
        user1.api_key, wallet1.address, wallet2.address, 0.5
    )
    transaction2 = transactions.make_transaction(
        user2.api_key, wallet2.address, wallet1.address, 0.5
    )

    assert transactions.get_wallet_transactions(user1.api_key, wallet1.address) == [
        transaction1,
        transaction2,
    ]
    db.close_database()
