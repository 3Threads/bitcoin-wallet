from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass
class User:
    api_key: str


class UserRepository(Protocol):
    def create(self, api_key: str) -> None:
        pass

    def check_key(self, api_key: str) -> bool:
        pass
