from uuid import uuid4

from core.errors import InvalidApiKeyError, WalletDoesNotExistError, WalletsLimitError
from core.user import generate_api_key
from infra.constants import WALLETS_LIMIT


def test_wallet_does_not_exist_error() -> None:
    unknown_id = uuid4()
    json = WalletDoesNotExistError(str(unknown_id)).get_error_json_response()
    assert json.status_code == 404
    assert (
        json.body.decode("utf-8")
        == '{"error":{"message":"Wallet with address<'
        + str(unknown_id)
        + '> does not exist."}}'
    )


def test_invalid_api_key_error() -> None:
    api_key = generate_api_key()
    json = InvalidApiKeyError(str(api_key)).get_error_json_response()
    assert json.status_code == 401
    assert (
        json.body.decode("utf-8")
        == '{"error":{"message":"Invalid API key: ' + str(api_key) + '"}}'
    )


def test_wallets_limit_error() -> None:
    api_key = generate_api_key()
    json = WalletsLimitError(str(api_key)).get_error_json_response()
    assert json.status_code == 409
    assert (
        json.body.decode("utf-8")
        == '{"error":{"message":"User<'
        + str(api_key)
        + "> reached wallets limit("
        + str(WALLETS_LIMIT)
        + ')."}}'
    )
