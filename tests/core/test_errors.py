from uuid import uuid4

from core.errors import WalletDoesNotExistError


def test_wallet_does_not_exist_error() -> None:
    unknown_id = uuid4()
    json = WalletDoesNotExistError(str(unknown_id)).get_error_json_response(404)
    assert json.status_code == 404
    assert (
            json.body.decode("utf-8")
            == '{"error":{"message":"Wallet with address<'
            + str(unknown_id)
            + '> does not exist."}}'
    )
