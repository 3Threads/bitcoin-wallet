from dataclasses import dataclass
from uuid import UUID

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from infra.constants import WALLETS_LIMIT


class ErrorMessageResponse(BaseModel):
    message: str


class ErrorMessageEnvelope(BaseModel):
    error: ErrorMessageResponse


@dataclass
class DoesNotExistError(Exception):
    name: str
    field: str
    value: str

    def get_error_json_response(self, code: int = 404) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    "message": f"{self.name} with {self.field}<{self.value}>"
                    f" does not exist."
                }
            },
        )


@dataclass
class InvalidApiKeyError(Exception):
    api_key: str

    def get_error_json_response(self, code: int = 401) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={"error": {"message": f"Invalid API key: {self.api_key}"}},
        )


@dataclass
class WalletsLimitError(Exception):
    api_key: str

    def get_error_json_response(self, code: int = 409) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    "message": f"User<{self.api_key}> "
                    f"reached wallets limit({WALLETS_LIMIT})."
                }
            },
        )


@dataclass
class WalletPermissionError(Exception):
    wallet_address: UUID

    def get_error_json_response(self, code: int = 403) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    "message": f"User does not have wallet<{self.wallet_address}>."
                }
            },
        )


@dataclass
class NotEnoughBitcoinError(Exception):
    wallet_address: UUID

    def get_error_json_response(self, code: int = 409) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    "message": f"Not enough bitcoin on the wallet with address"
                    f"<{self.wallet_address}>."
                }
            },
        )


@dataclass
class TransactionBetweenSameWalletError(Exception):
    def get_error_json_response(self, code: int = 405) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {"message": "Transaction between one wallet is restricted."}
            },
        )


@dataclass
class EmailAlreadyExistError(Exception):
    email: str

    def get_error_json_response(self, code: int = 409) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={"error": {"message": f"The email: {self.email} already exists."}},
        )
