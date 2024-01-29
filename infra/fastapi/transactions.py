from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import ErrorMessageEnvelope, NotEnoughBitcoinError, TransactionBetweenSameWalletError, \
    WalletPermissionError, DoesNotExistError, InvalidApiKeyError
from core.transaction import Transaction
from infra.fastapi.dependables import ApiKey, TransactionRepositoryDependable

transactions_api = APIRouter(tags=["Transactions"])


class TransactionItem(BaseModel):
    from_address: UUID
    to_address: UUID
    transaction_amount: float
    transaction_fee: float


class MakeTransactionItem(BaseModel):
    from_address: UUID
    to_address: UUID
    transaction_amount: float


class TransactionItemEnvelope(BaseModel):
    transaction: TransactionItem


class TransactionsListEnvelope(BaseModel):
    transactions: list[TransactionItem]


@transactions_api.post(
    "/transactions",
    status_code=201,
    response_model=TransactionItemEnvelope,
    responses={409: {"model": ErrorMessageEnvelope}},
)
def make_transaction(
        api_key: ApiKey, request: MakeTransactionItem, transactions: TransactionRepositoryDependable
) -> dict[str, Transaction] | JSONResponse:
    try:
        transaction = transactions.make_transaction(api_key, **request.model_dump())
        return {"transaction": transaction}
    except NotEnoughBitcoinError as e:
        return e.get_error_json_response()
    except TransactionBetweenSameWalletError as e:
        return e.get_error_json_response()
    except WalletPermissionError as e:
        return e.get_error_json_response()
    except DoesNotExistError as e:
        return e.get_error_json_response()
    except InvalidApiKeyError as e:
        return e.get_error_json_response()


@transactions_api.get(
    "/transactions",
    status_code=200,
    response_model=TransactionsListEnvelope,
)
def read_all_transactions(api_key: ApiKey, transactions: TransactionRepositoryDependable
                          ) -> dict[str, list[Transaction]] | JSONResponse:
    try:
        return {"transactions": transactions.read_all(api_key)}
    except InvalidApiKeyError as e:
        return e.get_error_json_response()
