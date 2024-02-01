from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from infra.constants import STARTING_BITCOIN_AMOUNT


@dataclass
class Wallet:
    user_id: UUID
    address: UUID = field(default_factory=uuid4)
    balance: float = STARTING_BITCOIN_AMOUNT

    def get_balance(self) -> float:
        return float("{:.8f}".format(self.balance))

class WalletRepository(Protocol):
    def create(self, api_key: str) -> Wallet:
        pass

    def read(self, address: str, api_key: str) -> Wallet:
        pass

    def read_all(self, api_key: str) -> list[Wallet]:
        pass

    def update_balance(self, address: UUID, new_balance: float) -> None:
        pass
