from dataclasses import dataclass
from sqlite3 import Connection, Cursor, IntegrityError
from uuid import UUID

from core.errors import EmailAlreadyExistError, InvalidApiKeyError
from core.user import User


@dataclass
class UsersDatabase:
    con: Connection
    cur: Cursor

    def create(self, email: str) -> EmailAlreadyExistError | User:
        user = User(email=email)
        try:
            self.cur.executemany(
                "INSERT INTO USERS(ID, EMAIL, API_KEY) VALUES (?, ?, ?)",
                [(str(user.id), user.email, user.api_key)],
            )
        except IntegrityError:
            raise EmailAlreadyExistError(user.email)

        self.con.commit()
        return user

    def try_authorization(self, api_key: str) -> User:
        self.cur.execute("SELECT * FROM USERS WHERE API_KEY = ?", [api_key])

        result = self.cur.fetchone()
        if result is not None and result[0] is not None:
            return User(result[1], UUID(result[0]), result[2])
        else:
            raise InvalidApiKeyError(api_key)
