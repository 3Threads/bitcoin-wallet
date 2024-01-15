from dataclasses import dataclass

from core.transaction import Transaction


@dataclass
class TransactionInMemory:
    def make_transaction(self, from_api_key: str, from_address: str, to_address: str,
                         transaction_amount: float) -> Transaction:
        pass

    def read_all(self, api_key: str) -> list[Transaction]:
        pass

