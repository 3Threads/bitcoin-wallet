from dataclasses import dataclass, field

from core.errors import DoesNotExistError, InvalidApiKeyError
from core.user import User


@dataclass
class UserInMemory:
    users: dict[str, User] = field(default_factory=dict)

    def create(self) -> User:
        user = User()
        self.users[user.api_key] = user
        return user

    def try_authorization(self, api_key: str) -> User:
        try:
            return self.users[api_key]
        except KeyError:
            raise InvalidApiKeyError(api_key)
