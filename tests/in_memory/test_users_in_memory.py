import secrets
from unittest.mock import ANY

import pytest

from core.errors import InvalidApiKeyError
from infra.constants import TOKEN_HEX_BYTES_NUM
from infra.in_memory.users import UsersInMemory


def test_create_user_in_memory() -> None:
    users = UsersInMemory()
    user = users.create()

    assert user.api_key == ANY
    assert user.id == ANY


def test_read_correct_user_in_memory() -> None:
    users = UsersInMemory()
    user = users.create()

    result_user = users.try_authorization(user.api_key)

    assert result_user == user


def test_invalid_api_key_in_memory() -> None:
    users = UsersInMemory()

    with pytest.raises(InvalidApiKeyError):
        users.try_authorization(secrets.token_hex(TOKEN_HEX_BYTES_NUM))
