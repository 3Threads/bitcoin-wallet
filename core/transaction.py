from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass
class Transaction:
    from_address: UUID
    to_address: UUID
    transaction_amount: float
    transaction_fee: float


class TransactionRepository(Protocol):
    def make_transaction(self, from_api_key: str, from_address: UUID, to_address: UUID,
                         transaction_amount: float) -> Transaction:
        pass

    def read_all(self, api_key: str) -> list[Transaction]:
        pass

    def get_wallet_transactions(self, api_key: str, address: UUID) -> list[Transaction]:
        pass
