from dataclasses import dataclass, field

from core.errors import DoesNotExistError
from core.user import User


@dataclass
class UserInMemory:
    users: dict[str, User] = field(default_factory=dict)

    def create(self) -> User:
        user = User()
        self.users[user.api_key] = user
        return user

    def get_user(self, api_key: str) -> User:
        try:
            return self.users[api_key]
        except KeyError:
            raise DoesNotExistError("User", "API_KEY", api_key)
