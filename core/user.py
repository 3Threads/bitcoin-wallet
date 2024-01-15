import secrets
from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


def generate_api_key():
    return secrets.token_hex(32)


@dataclass
class User:
    id: UUID = field(default_factory=uuid4)
    api_key: str = field(default_factory=generate_api_key)


class UserRepository(Protocol):
    def create(self) -> User:
        pass

    def try_authorization(self, api_key: str) -> User:
        pass
