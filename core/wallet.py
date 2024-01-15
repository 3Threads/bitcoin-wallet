from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass
class Wallet:
    user_api_key: str
    address: UUID
    balance: float


class WalletRepository(Protocol):
    def create(self, api_key: str) -> Wallet:
        pass

    def read(self, address: str, api_key: str) -> Wallet:
        pass

    def read_all(self, api_key: str) -> list[Wallet]:
        pass
