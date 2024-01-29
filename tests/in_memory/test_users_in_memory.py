import secrets
from unittest.mock import ANY

import pytest

from core.errors import InvalidApiKeyError, EmailAlreadyExistError
from core.user import generate_api_key
from infra.constants import TOKEN_HEX_BYTES_NUM
from infra.in_memory.users import UsersInMemory


def test_create_user_in_memory() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")

    assert user.api_key == ANY
    assert user.id == ANY


def test_create_same_user_in_memory() -> None:
    users = UsersInMemory()
    email = "test@gmail.com"
    users.create(email=email)

    with pytest.raises(EmailAlreadyExistError):
        users.create(email=email)


def test_read_correct_user_in_memory() -> None:
    users = UsersInMemory()
    user = users.create(email="test@gmail.com")

    result_user = users.try_authorization(user.api_key)

    assert result_user == user


def test_invalid_api_key_in_memory() -> None:
    users = UsersInMemory()

    with pytest.raises(InvalidApiKeyError):
        users.try_authorization(generate_api_key())
