from dataclasses import dataclass

from fastapi.responses import JSONResponse
from pydantic import BaseModel


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
