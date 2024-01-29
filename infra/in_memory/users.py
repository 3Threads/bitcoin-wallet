from dataclasses import dataclass, field
from uuid import UUID

from core.errors import EmailAlreadyExistError, InvalidApiKeyError
from core.user import User


@dataclass
class UsersInMemory:
    users: dict[UUID, User] = field(default_factory=dict)

    def create(self, email: str) -> EmailAlreadyExistError | User:
        for (user_id, user) in self.users.items():
            if user.email == email:
                raise EmailAlreadyExistError(email)

        user = User(email=email)
        self.users[user.id] = user
        return user

    def try_authorization(self, api_key: str) -> User:
        for user in self.users.values():
            if user.api_key == api_key:
                return user
        raise InvalidApiKeyError(api_key)
