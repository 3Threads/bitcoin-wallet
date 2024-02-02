import math
from dataclasses import dataclass, field
from uuid import UUID

from core.errors import NotEnoughBitcoinError, TransactionBetweenSameWalletError
from core.transaction import Transaction
from infra.constants import MINIMUM_AMOUNT_OF_BITCOIN
from infra.in_memory.users import UsersInMemory
from infra.in_memory.wallets import WalletsInMemory


@dataclass
class TransactionsInMemory:
    users: UsersInMemory
    wallets: WalletsInMemory
    transactions: list[Transaction] = field(default_factory=list)

    def make_transaction(
        self,
        from_api_key: str,
        from_address: UUID,
        to_address: UUID,
        transaction_amount: float,
    ) -> Transaction:
        if from_address == to_address:
            raise TransactionBetweenSameWalletError()

        from_wallet = self.wallets.read(from_address, from_api_key)
        to_wallet = self.wallets.read(to_address, from_api_key, False)

        transaction_amount = math.ceil(transaction_amount * 10**8) / 10**8

        if from_wallet.get_balance() < transaction_amount:
            raise NotEnoughBitcoinError(from_address)

        from_new_balance = from_wallet.get_balance() - transaction_amount
        to_new_balance = to_wallet.get_balance() + transaction_amount

        fee = 0
        if from_wallet.user_id != to_wallet.user_id:
            fee = transaction_amount * 1.5 / 100
        if fee < MINIMUM_AMOUNT_OF_BITCOIN and fee != 0:
            fee = MINIMUM_AMOUNT_OF_BITCOIN
        to_new_balance -= fee

        self.wallets.update_balance(from_address, from_new_balance)
        self.wallets.update_balance(to_address, to_new_balance)

        transaction = Transaction(from_address, to_address, transaction_amount, fee)
        self.transactions.append(transaction)
        return transaction

    def read_all(self, api_key: str) -> list[Transaction]:
        user = self.users.try_authorization(api_key)

        transactions = []
        for transaction in self.transactions:
            from_wallet = self.wallets.read(transaction.from_address, api_key, False)
            to_wallet = self.wallets.read(transaction.to_address, api_key, False)
            if from_wallet.user_id == user.id or to_wallet.user_id == user.id:
                transactions.append(transaction)

        return transactions

    def get_wallet_transactions(self, api_key: str, address: UUID) -> list[Transaction]:
        self.users.try_authorization(api_key)
        self.wallets.read(address, api_key, True)

        transactions = []
        for transaction in self.transactions:
            if transaction.from_address == address or transaction.to_address == address:
                transactions.append(transaction)

        return transactions
