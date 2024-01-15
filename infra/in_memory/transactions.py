from dataclasses import dataclass, field
from uuid import UUID

from core.transaction import Transaction
from core.wallet import Wallet


@dataclass
class TransactionInMemory:
    transactions: dict[str, list[Transaction]] = field(default_factory=dict)

    def make_transaction(self, from_api_key: UUID, from_address: UUID, to_address: UUID,
                         transaction_amount: float) -> Transaction:
        pass

    def read_all(self, api_key: str) -> list[Transaction]:
        pass

    def get_wallet_transactions(self, api_key: str, wallet: Wallet) -> list[Transaction]:
        pass