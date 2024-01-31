import os

import pytest

from core.errors import InvalidApiKeyError
from core.statistic import Statistic
from core.user import generate_api_key
from infra.constants import ADMIN_API_KEY, SQL_FILE_TEST
from infra.in_memory.statistics import StatisticsInMemory
from infra.sqlite.database_connect import Database
from infra.sqlite.statistics import StatisticsDatabase
from infra.sqlite.transactions import TransactionsDataBase
from infra.sqlite.users import UsersDatabase
from infra.sqlite.wallets import WalletsDatabase


@pytest.fixture
def db() -> Database:
    db = Database(":memory:", os.path.abspath(SQL_FILE_TEST))
    db.initial()
    return db


def test_get_empty_statistics_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    statistics = StatisticsDatabase(db.get_connection(), db.get_cursor(), transactions)

    assert statistics.get_statistics(ADMIN_API_KEY) == Statistic(0, 0.0)


def test_get_statistics_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    wallet1 = wallets.create(user1.api_key)
    wallet2 = wallets.create(user2.api_key)

    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    transactions.make_transaction(user1.api_key, wallet1.address, wallet2.address, 1)
    transactions.make_transaction(user2.api_key, wallet2.address, wallet1.address, 1)

    statistics = StatisticsDatabase(db.get_connection(), db.get_cursor(), transactions)

    assert statistics.get_statistics(ADMIN_API_KEY) == Statistic(2, 0.03)


def test_get_statistics_unknown_api_key_in_memory(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    wallets = WalletsDatabase(db.get_connection(), db.get_cursor(), users)
    transactions = TransactionsDataBase(
        db.get_connection(), db.get_cursor(), wallets, users
    )
    statistics = StatisticsDatabase(db.get_connection(), db.get_cursor(), transactions)

    with pytest.raises(InvalidApiKeyError):
        statistics.get_statistics(generate_api_key())
