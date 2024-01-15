from dataclasses import dataclass, field

from core.errors import AlreadyExistError
import secrets


@dataclass
class UserInMemory:
    keys: set = field(default_factory=set)

    def create(self, api_key: str = secrets.token_hex(32)) -> None:
        if api_key in self.keys:
            raise AlreadyExistError("User", "API_KEY", api_key)
        self.keys.add(api_key)

    def check_key(self, api_key: str) -> bool:
        if api_key in self.keys:
            return True
        return False
