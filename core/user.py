import secrets
from dataclasses import dataclass, field
from typing import Protocol


def generate_api_key():
    return secrets.token_hex(32)


@dataclass
class User:
    api_key: str = field(default_factory=generate_api_key)


class UserRepository(Protocol):
    def create(self) -> User:
        pass

    def get_user(self, api_key: str) -> User:
        pass
