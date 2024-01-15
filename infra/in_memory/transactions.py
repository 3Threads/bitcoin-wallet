from dataclasses import dataclass, field
from uuid import UUID

from core.transaction import Transaction
from infra.in_memory.users import UsersInMemory
from infra.in_memory.wallets import WalletsInMemory


@dataclass
class TransactionsInMemory:
    users: UsersInMemory
    wallets: WalletsInMemory
    transactions: list[Transaction] = field(default_factory=list)

    def make_transaction(self, from_api_key: str, from_address: UUID, to_address: UUID,
                         transaction_amount: float) -> Transaction:
        from_wallet = self.wallets.read(from_address, from_api_key)
        to_wallet = self.wallets.read(to_address, from_api_key)

        from_wallet.balance -= transaction_amount
        to_wallet.balance += transaction_amount

        fee = 0
        if from_wallet.user_id != to_wallet.user_id:
            fee = transaction_amount * 101.5 / 100
        to_wallet.balance -= fee

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
