from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from core.errors import (
    ErrorMessageEnvelope,
    InvalidApiKeyError,
    WalletDoesNotExistError,
    WalletPermissionError,
    WalletsLimitError,
)
from core.wallet import Wallet
from infra.fastapi.dependables import (
    ApiKey,
    ConverterDependable,
    TransactionRepositoryDependable,
    WalletRepositoryDependable,
)
from infra.fastapi.transactions import TransactionsListEnvelope

wallets_api = APIRouter(tags=["Wallets"])


class WalletItem(BaseModel):
    address: UUID
    balance_btc: float
    balance_usd: float


class WalletItemEnvelope(BaseModel):
    wallet: WalletItem


class WalletListEnvelope(BaseModel):
    wallets: list[WalletItem]


@wallets_api.post(
    "/wallets",
    status_code=201,
    response_model=WalletItemEnvelope,
    responses={
        401: {"model": ErrorMessageEnvelope},
        409: {"model": ErrorMessageEnvelope},
    },
)
def create_wallet(
    api_key: ApiKey, wallets: WalletRepositoryDependable, converter: ConverterDependable
):
    try:
        wallet: Wallet = wallets.create(api_key)
        balance_usd = wallet.balance * converter.get_rate()
        return {
            "wallet": {
                "address": wallet.address,
                "balance_btc": wallet.balance,
                "balance_usd": balance_usd,
            }
        }
    except InvalidApiKeyError as e:
        return e.get_error_json_response(401)
    except WalletsLimitError as e:
        return e.get_error_json_response(409)


@wallets_api.get(
    "/wallets/{address}",
    status_code=200,
    response_model=WalletItemEnvelope,
    responses={
        401: {"model": ErrorMessageEnvelope},
        403: {"model": ErrorMessageEnvelope},
        404: {"model": ErrorMessageEnvelope},
    },
)
def read_wallet(
    address: UUID,
    api_key: ApiKey,
    wallets: WalletRepositoryDependable,
    converter: ConverterDependable,
):
    try:
        wallet: Wallet = wallets.read(address, api_key)
        balance_usd = wallet.balance * converter.get_rate()
        return {
            "wallet": {
                "address": wallet.address,
                "balance_btc": wallet.balance,
                "balance_usd": balance_usd,
            }
        }
    except InvalidApiKeyError as e:
        return e.get_error_json_response(401)
    except WalletDoesNotExistError as e:
        return e.get_error_json_response(404)
    except WalletPermissionError as e:
        return e.get_error_json_response(403)


@wallets_api.get(
    "/wallets/{address}/transactions",
    status_code=200,
    response_model=TransactionsListEnvelope,
    responses={
        401: {"model": ErrorMessageEnvelope},
        403: {"model": ErrorMessageEnvelope},
        404: {"model": ErrorMessageEnvelope},
    },
)
def get_wallet_transactions(
    address: UUID, api_key: ApiKey, transactions: TransactionRepositoryDependable
):
    try:
        transactions = transactions.get_wallet_transactions(api_key, address)
        return {"transactions": transactions}
    except InvalidApiKeyError as e:
        return e.get_error_json_response(401)
    except WalletDoesNotExistError as e:
        return e.get_error_json_response(404)
    except WalletPermissionError as e:
        return e.get_error_json_response(403)
