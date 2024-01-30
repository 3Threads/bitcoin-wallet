from unittest.mock import ANY
from uuid import uuid4

import pytest

from core.errors import (
    DoesNotExistError,
    InvalidApiKeyError,
    WalletPermissionError,
    WalletsLimitError,
)
from core.user import generate_api_key
from infra.constants import STARTING_BITCOIN_AMOUNT, WALLETS_LIMIT
from infra.in_memory.users import UsersInMemory
from infra.in_memory.wallets import WalletsInMemory


def test_create_wallet_in_memory() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")

    wallets = WalletsInMemory(users)
    wallet = wallets.create(user.api_key)

    assert wallet.user_id == user.id
    assert wallet.address == ANY
    assert wallet.balance == STARTING_BITCOIN_AMOUNT


def test_create_wallet_reach_limit_in_memory() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")

    wallets = WalletsInMemory(users)
    for i in range(WALLETS_LIMIT):
        wallets.create(user.api_key)

    with pytest.raises(WalletsLimitError):
        wallets.create(user.api_key)


def test_create_wallet_with_unknown_key_in_memory() -> None:
    wallets = WalletsInMemory(UsersInMemory())

    with pytest.raises(InvalidApiKeyError):
        wallets.create(generate_api_key())


def test_read_wallet_in_memory() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")

    wallets = WalletsInMemory(users)
    wallet = wallets.create(user.api_key)

    result_wallet = wallets.read(wallet.address, user.api_key)

    assert result_wallet == wallet


def test_read_wallet_with_wrong_key_in_memory() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")

    wallets = WalletsInMemory(users)
    wallet = wallets.create(user.api_key)

    with pytest.raises(InvalidApiKeyError):
        wallets.read(wallet.address, generate_api_key())


def test_read_unknown_wallet_in_memory() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")

    wallets = WalletsInMemory(users)

    with pytest.raises(DoesNotExistError):
        wallets.read(uuid4(), user.api_key)


def test_read_others_wallet_in_memory() -> None:
    users = UsersInMemory()
    user1 = users.create(email="test@gmail.com")
    user2 = users.create(email="test1@gmail.com")

    wallets = WalletsInMemory(users)
    wallet = wallets.create(user1.api_key)

    with pytest.raises(WalletPermissionError):
        wallets.read(wallet.address, user2.api_key)


def test_read_wallet_ignore_permission_in_memory() -> None:
    users = UsersInMemory()
    user1 = users.create(email="test@gmail.com")
    user2 = users.create(email="test1@gmail.com")

    wallets = WalletsInMemory(users)
    wallet = wallets.create(user1.api_key)

    result_wallet = wallets.read(wallet.address, user2.api_key, False)
    assert result_wallet == wallet


def test_update_balance_in_memory() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")
    wallets = WalletsInMemory(users)
    wallet = wallets.create(user.api_key)
    wallets.update_balance(wallet.address, 100)

    assert wallets.read(wallet.address, user.api_key).balance == 100


def test_read_all() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")

    wallets = WalletsInMemory(users)
    wallet1 = wallets.create(user.api_key)
    wallet2 = wallets.create(user.api_key)

    wallets.update_balance(wallet1.address, 100)
    wallets.update_balance(wallet2.address, 200)

    all_wallets = wallets.read_all(user.api_key)

    assert len(all_wallets) == 2
    assert all_wallets[0].balance == 100
    assert all_wallets[1].balance == 200
    assert all_wallets[1] == wallet2
    assert all_wallets[0] == wallet1
