import pytest

from core.errors import InvalidApiKeyError
from core.statistic import Statistic
from core.user import generate_api_key
from infra.constants import ADMIN_API_KEY
from infra.in_memory.statistics import StatisticsInMemory
from infra.in_memory.transactions import TransactionsInMemory
from infra.in_memory.users import UsersInMemory
from infra.in_memory.wallets import WalletsInMemory


def test_get_empty_statistics_in_memory() -> None:
    users = UsersInMemory()
    wallets = WalletsInMemory(users)
    transactions = TransactionsInMemory(users, wallets)
    statistics = StatisticsInMemory(transactions)

    assert statistics.get_statistics(ADMIN_API_KEY) == Statistic(0, 0.0)


def test_get_statistics_in_memory() -> None:
    users = UsersInMemory()
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsInMemory(users)
    wallet1 = wallets.create(user1.api_key)
    wallet2 = wallets.create(user2.api_key)

    transactions = TransactionsInMemory(users, wallets)
    transactions.make_transaction(user1.api_key, wallet1.address, wallet2.address, 1)
    transactions.make_transaction(user2.api_key, wallet2.address, wallet1.address, 1)

    statistics = StatisticsInMemory(transactions)

    assert statistics.get_statistics(ADMIN_API_KEY) == Statistic(2, 0.03)


def test_get_statistics_unknown_api_key_in_memory() -> None:
    users = UsersInMemory()
    wallets = WalletsInMemory(users)
    transactions = TransactionsInMemory(users, wallets)
    statistics = StatisticsInMemory(transactions)

    with pytest.raises(InvalidApiKeyError):
        statistics.get_statistics(generate_api_key())
