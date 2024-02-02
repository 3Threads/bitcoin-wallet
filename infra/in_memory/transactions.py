from dataclasses import dataclass, field
from uuid import UUID

from core.transaction import Transaction, TransactionRepository
from infra.in_memory.users import UsersInMemory
from infra.in_memory.wallets import WalletsInMemory


@dataclass
class TransactionsInMemory(TransactionRepository):
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
        transaction = self._prepare_transaction(
            from_api_key, from_address, to_address, transaction_amount, self.wallets
        )
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
