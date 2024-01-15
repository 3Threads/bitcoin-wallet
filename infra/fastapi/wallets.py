from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from core.errors import ErrorMessageEnvelope, WalletsLimitError, ApiKeyDoesNotExistError, \
    AddressDoesNotExistError
from infra.fastapi.dependables import ApiKey, WalletRepositoryDependable, TransactionRepositoryDependable
from infra.fastapi.transactions import TransactionsListEnvelope

wallets_api = APIRouter(tags=["Wallets"])


class WalletItem(BaseModel):
    user_api_key: str
    address: UUID
    balance: float


class WalletItemEnvelope(BaseModel):
    wallet: WalletItem


class WalletListEnvelope(BaseModel):
    wallets: list[WalletItem]


@wallets_api.post(
    "/wallets",
    status_code=201,
    response_model=WalletItemEnvelope,
    responses={404: {"model": ErrorMessageEnvelope}},
)
def create_wallet(
        api_key: ApiKey, wallets: WalletRepositoryDependable
):
    try:
        return {"wallet": wallets.create(api_key)}
    except ApiKeyDoesNotExistError as e:
        return e.get_error_json_response(404)
    except WalletsLimitError as e:
        return e.get_error_json_response()


@wallets_api.get(
    "/wallets/{address}",
    status_code=201,
    response_model=WalletItemEnvelope,
    responses={409: {"model": ErrorMessageEnvelope}},
)
def read_wallet(
        address: str, api_key: ApiKey, wallets: WalletRepositoryDependable
):
    try:
        return {"wallet": wallets.read(address, api_key)}
    except ApiKeyDoesNotExistError as e:
        return e.get_error_json_response(404)
    except AddressDoesNotExistError as e:
        return e.get_error_json_response(404)

@wallets_api.get(
    "/wallets/{address}/transactions",
    status_code=201,
    response_model=TransactionsListEnvelope,
    responses={409: {"model": ErrorMessageEnvelope}},
)
def get_wallet_transactions(
        address: str, api_key: ApiKey, transactions: TransactionRepositoryDependable, wallets: WalletRepositoryDependable
):
    try:
        transactions = transactions.get_wallet_transactions(api_key, wallets.read(api_key, address))
        return {"transactions": transactions}
    except ApiKeyDoesNotExistError as e:
        return e.get_error_json_response(404)
    except AddressDoesNotExistError as e:
        return e.get_error_json_response(404)