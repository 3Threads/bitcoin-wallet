import secrets
from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from infra.constants import TOKEN_HEX_BYTES_NUM


def generate_api_key() -> str:
    return secrets.token_hex(TOKEN_HEX_BYTES_NUM)


@dataclass
class User:
    email: str
    id: UUID = field(default_factory=uuid4)
    api_key: str = field(default_factory=generate_api_key)


class UserRepository(Protocol):
    def create(self, email: str) -> User:
        pass

    def try_authorization(self, api_key: str) -> User:
        pass
