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
class AlreadyExistError(Exception):
    name: str
    field: str
    value: str

    def get_error_json_response(self, code: int = 409) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    "message": f"{self.name} with {self.field}<{self.value}>"
                               f" already exists."
                }
            },
        )


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
            content={
                "error": {
                    "message": f"Invalid API key: {self.api_key}"
                }
            },
        )


@dataclass
class ClosedReceiptError(Exception):
    name: str
    field: str
    value: str

    def get_error_json_response(self, code: int = 403) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    "message": f"{self.name} with {self.field}<{self.value}> is closed."
                }
            },
        )


@dataclass
class WalletsLimitError(Exception):
    api_key: str

    def get_error_json_response(self, code: int = 403) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    f"message": f"User<{self.api_key}> reached wallets limit({WALLETS_LIMIT})."
                }
            },
        )


@dataclass
class WalletPermissionError(Exception):
    wallet_address: UUID

    def get_error_json_response(self, code: int = 404) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    f"message": f"User does not have wallet<{self.wallet_address}>."
                }
            },
        )


@dataclass
class NotEnoughBitcoinError(Exception):
    wallet_address: UUID

    def get_error_json_response(self, code: int = 404) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    f"message": f"Not enough bitcoin on the wallet with address<{self.wallet_address}>."
                }
            },
        )


@dataclass
class TransactionBetweenSameWalletError(Exception):
    def get_error_json_response(self, code: int = 404) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    f"message": f"Transaction between one wallet is restricted."
                }
            },
        )


@dataclass
class EmailAlreadyExistsError(Exception):
    email: str

    def get_error_json_response(self, code: int = 404) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    f"message": f"The email: {self.email} already exists."
                }
            },
        )
