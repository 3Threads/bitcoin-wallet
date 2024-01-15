from dataclasses import dataclass
from typing import Protocol


@dataclass
class Transaction:
    from_address: str
    to_address: str
    transaction_amount: float
    transaction_fee: float


class TransactionRepository(Protocol):
    def make_transaction(self, from_api_key: str, from_address: str, to_address: str,
                         transaction_amount: float) -> Transaction:
        pass

    def read_all(self, api_key: str) -> list[Transaction]:
        pass
