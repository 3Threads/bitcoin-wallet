import os
from unittest.mock import ANY

import pytest

from core.errors import EmailAlreadyExistError, InvalidApiKeyError
from core.user import generate_api_key
from infra.constants import SQL_FILE_TEST
from infra.sqlite.database_connect import Database
from infra.sqlite.users import UsersDatabase


@pytest.fixture
def db() -> Database:
    db = Database(":memory:", os.path.abspath(SQL_FILE_TEST))
    db.initial()
    return db


def test_insert_user(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create("test@gmail.com")

    assert user.api_key == ANY
    assert user.id == ANY
    db.close_database()


def test_create_same_user_twice(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    email = "test@gmail.com"
    users.create(("%s" % email))

    with pytest.raises(EmailAlreadyExistError):
        users.create(email)
    db.close_database()


def test_read_correct_user(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())
    user = users.create("test@gmail.com")

    result_user = users.try_authorization(user.api_key)

    assert result_user == user
    db.close_database()


def test_invalid_api_key(db: Database) -> None:
    users = UsersDatabase(db.get_connection(), db.get_cursor())

    with pytest.raises(InvalidApiKeyError):
        users.try_authorization(generate_api_key())
    db.close_database()
