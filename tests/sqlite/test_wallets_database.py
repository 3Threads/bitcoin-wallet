import os
from unittest.mock import ANY
from uuid import uuid4

import pytest

from core.errors import DoesNotExistError, WalletsLimitError, InvalidApiKeyError, \
    WalletPermissionError
from core.user import generate_api_key
from infra.constants import STARTING_BITCOIN_AMOUNT, WALLETS_LIMIT, SQL_FILE_TEST
from infra.in_memory.users import UsersInMemory
from infra.in_memory.wallets import WalletsInMemory
from infra.sqlite.database_connect import Database
from infra.sqlite.users import UsersDatabase
from infra.sqlite.wallets import WalletsDatabase


@pytest.fixture
def db() -> Database:
    db = Database(":memory:", os.path.abspath(SQL_FILE_TEST))
    db.initial()
    return db


def test_create_wallet_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create(email="test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    wallet = wallets.create(user.api_key)

    assert wallet.user_id == user.id
    assert wallet.address == ANY
    assert wallet.balance == STARTING_BITCOIN_AMOUNT

    db.close_database()


def test_create_wallet_reach_limit_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create(email="test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    for i in range(WALLETS_LIMIT):
        wallets.create(user.api_key)

    with pytest.raises(WalletsLimitError):
        wallets.create(user.api_key)
    db.close_database()


def test_create_wallet_with_unknown_key_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    with pytest.raises(InvalidApiKeyError):
        wallets.create(generate_api_key())
    db.close_database()


def test_read_wallet_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create(email="test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    wallet = wallets.create(user.api_key)

    result_wallet = wallets.read(wallet.address, user.api_key)

    assert result_wallet == wallet
    db.close_database()


def test_read_wallet_with_wrong_key_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create(email="test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    wallet = wallets.create(user.api_key)

    with pytest.raises(InvalidApiKeyError):
        wallets.read(wallet.address, generate_api_key())
    db.close_database()


def test_read_unknown_wallet_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create(email="test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    with pytest.raises(DoesNotExistError):
        wallets.read(uuid4(), user.api_key)
    db.close_database()


def test_read_others_wallet_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create(email="test@gmail.com")
    user2 = users.create(email="test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    wallet = wallets.create(user1.api_key)

    with pytest.raises(WalletPermissionError):
        wallets.read(wallet.address, user2.api_key)
    db.close_database()


def test_read_wallet_ignore_permission_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create(email="test@gmail.com")
    user2 = users.create(email="test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)

    wallet = wallets.create(user1.api_key)

    result_wallet = wallets.read(wallet.address, user2.api_key, False)
    assert result_wallet == wallet

    db.close_database()


def test_update_balance_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create(email="test@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    wallet = wallets.create(user.api_key)

    wallets.update_balance(wallet.address, 100)

    assert wallets.read(wallet.address, user.api_key).balance == 100

    db.close_database()

