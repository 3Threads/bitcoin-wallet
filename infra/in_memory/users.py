from dataclasses import dataclass, field
from uuid import UUID

from core.errors import DoesNotExistError, InvalidApiKeyError
from core.user import User


@dataclass
class UsersInMemory:
    users: dict[UUID, User] = field(default_factory=dict)

    def create(self) -> User:
        user = User()
        self.users[user.id] = user
        return user

    def try_authorization(self, api_key: str) -> User:
        for user in self.users.values():
            if user.api_key == api_key:
                return user
        raise InvalidApiKeyError(api_key)
