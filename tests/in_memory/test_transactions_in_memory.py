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
from infra.constants import MINIMUM_AMOUNT_OF_BITCOIN
from infra.in_memory.transactions import TransactionsInMemory
from infra.in_memory.users import UsersInMemory
from infra.in_memory.wallets import WalletsInMemory


def test_make_transaction_in_memory() -> None:
    users = UsersInMemory()
    user = users.create("test@gmail.com")

    wallets = WalletsInMemory(users)
    from_wallet = wallets.create(user.api_key)
    to_wallet = wallets.create(user.api_key)

    transactions = TransactionsInMemory(users, wallets)
    transaction = transactions.make_transaction(
        user.api_key, from_wallet.address, to_wallet.address, 0.5
    )

    assert transaction.from_address == from_wallet.address
    assert transaction.to_address == to_wallet.address
    assert transaction.transaction_amount == 0.5
    assert transaction.transaction_fee == 0
    assert from_wallet.get_balance() == 0.5
    assert to_wallet.get_balance() == 1.5


def test_make_transaction_between_two_users_in_memory() -> None:
    users = UsersInMemory()
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsInMemory(users)
    from_wallet = wallets.create(user1.api_key)
    to_wallet = wallets.create(user2.api_key)

    transactions = TransactionsInMemory(users, wallets)
    transaction = transactions.make_transaction(
        user1.api_key, from_wallet.address, to_wallet.address, 1
    )

    assert transaction.from_address == from_wallet.address
    assert transaction.to_address == to_wallet.address
    assert transaction.transaction_amount == 1
    assert transaction.transaction_fee == 0.015
    assert from_wallet.get_balance() == 0
    assert to_wallet.get_balance() == 1.985


def test_transaction_less_then_one_satishi() -> None:
    users = UsersInMemory()
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsInMemory(users)
    from_wallet = wallets.create(user1.api_key)
    to_wallet = wallets.create(user2.api_key)

    transactions = TransactionsInMemory(users, wallets)
    transaction = transactions.make_transaction(
        user1.api_key,
        from_wallet.address,
        to_wallet.address,
        0.5 * MINIMUM_AMOUNT_OF_BITCOIN,
    )
    assert transaction.from_address == from_wallet.address
    assert transaction.to_address == to_wallet.address
    assert from_wallet.get_balance() == 1 - MINIMUM_AMOUNT_OF_BITCOIN
    assert to_wallet.get_balance() == 1


def test_double_transaction_with_less_then_one_satoshi_fee() -> None:
    users = UsersInMemory()
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsInMemory(users)
    from_wallet = wallets.create(user1.api_key)
    to_wallet = wallets.create(user2.api_key)

    transactions = TransactionsInMemory(users, wallets)
    transaction = transactions.make_transaction(
        user1.api_key,
        from_wallet.address,
        to_wallet.address,
        1 - 2 * MINIMUM_AMOUNT_OF_BITCOIN,
    )
    assert transaction.from_address == from_wallet.address
    assert transaction.to_address == to_wallet.address
    assert from_wallet.get_balance() == 2 * MINIMUM_AMOUNT_OF_BITCOIN
    assert to_wallet.get_balance() == 1.98499998

    transaction2 = transactions.make_transaction(
        user1.api_key,
        from_wallet.address,
        to_wallet.address,
        1.5 * MINIMUM_AMOUNT_OF_BITCOIN,
    )

    assert transaction2.from_address == from_wallet.address
    assert transaction2.to_address == to_wallet.address
    assert to_wallet.get_balance() == 1.98499999
    assert from_wallet.get_balance() == 0


def test_make_transaction_without_enough_balance_in_memory() -> None:
    users = UsersInMemory()
    user = users.create("test@gmail.com")

    wallets = WalletsInMemory(users)
    from_wallet = wallets.create(user.api_key)
    to_wallet = wallets.create(user.api_key)

    transactions = TransactionsInMemory(users, wallets)
    with pytest.raises(NotEnoughBitcoinError):
        transactions.make_transaction(
            user.api_key, from_wallet.address, to_wallet.address, 1.5
        )


def test_make_transaction_between_same_wallet_in_memory() -> None:
    users = UsersInMemory()
    user = users.create("test@gmail.com")

    wallets = WalletsInMemory(users)
    wallet = wallets.create(user.api_key)

    transactions = TransactionsInMemory(users, wallets)
    with pytest.raises(TransactionBetweenSameWalletError):
        transactions.make_transaction(user.api_key, wallet.address, wallet.address, 0.5)


def test_make_transaction_other_api_key_in_memory() -> None:
    users = UsersInMemory()
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsInMemory(users)
    transactions = TransactionsInMemory(users, wallets)

    with pytest.raises(WalletPermissionError):
        transactions.make_transaction(
            user2.api_key,
            wallets.create(user1.api_key).address,
            wallets.create(user2.api_key).address,
            0.5,
        )


def test_make_transaction_unknown_wallet_address_in_memory() -> None:
    users = UsersInMemory()
    wallets = WalletsInMemory(users)

    transactions = TransactionsInMemory(users, wallets)

    with pytest.raises(WalletDoesNotExistError):
        transactions.make_transaction(
            users.create("test@gmail.com").api_key, uuid4(), uuid4(), 0.5
        )


def test_make_transaction_unknown_api_key_in_memory() -> None:
    users = UsersInMemory()

    wallets = WalletsInMemory(users)

    transactions = TransactionsInMemory(users, wallets)

    with pytest.raises(InvalidApiKeyError):
        transactions.make_transaction(generate_api_key(), uuid4(), uuid4(), 0.5)


def test_read_all_transactions_empty_in_memory() -> None:
    users = UsersInMemory()
    user = users.create("test@gmail.com")

    wallets = WalletsInMemory(users)

    transactions = TransactionsInMemory(users, wallets)

    assert transactions.read_all(user.api_key) == []


def test_read_all_transactions_in_memory() -> None:
    users = UsersInMemory()
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsInMemory(users)
    wallet1 = wallets.create(user1.api_key)
    wallet2 = wallets.create(user2.api_key)

    transactions = TransactionsInMemory(users, wallets)
    transaction1 = transactions.make_transaction(
        user1.api_key, wallet1.address, wallet2.address, 0.5
    )
    transaction2 = transactions.make_transaction(
        user2.api_key, wallet2.address, wallet1.address, 0.5
    )

    assert transactions.read_all(user1.api_key) == [transaction1, transaction2]


def test_read_all_transactions_unknown_api_key_in_memory() -> None:
    users = UsersInMemory()
    wallets = WalletsInMemory(users)
    transactions = TransactionsInMemory(users, wallets)

    with pytest.raises(InvalidApiKeyError):
        transactions.read_all(generate_api_key())


def test_get_wallet_transactions_unknown_api_key_in_memory() -> None:
    users = UsersInMemory()

    wallets = WalletsInMemory(users)

    transactions = TransactionsInMemory(users, wallets)

    with pytest.raises(InvalidApiKeyError):
        transactions.get_wallet_transactions(generate_api_key(), uuid4())


def test_get_wallet_transactions_unknown_wallet_address_in_memory() -> None:
    users = UsersInMemory()
    wallets = WalletsInMemory(users)

    transactions = TransactionsInMemory(users, wallets)

    with pytest.raises(WalletDoesNotExistError):
        transactions.get_wallet_transactions(
            users.create("test@gmail.com").api_key, uuid4()
        )


def test_get_wallet_transactions_other_api_key_in_memory() -> None:
    users = UsersInMemory()
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsInMemory(users)
    transactions = TransactionsInMemory(users, wallets)

    with pytest.raises(WalletPermissionError):
        transactions.get_wallet_transactions(
            user2.api_key, wallets.create(user1.api_key).address
        )


def test_get_wallet_transactions_in_memory() -> None:
    users = UsersInMemory()
    user1 = users.create("test@gmail.com")
    user2 = users.create("test1@gmail.com")

    wallets = WalletsInMemory(users)
    wallet1 = wallets.create(user1.api_key)
    wallet2 = wallets.create(user2.api_key)

    transactions = TransactionsInMemory(users, wallets)
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
