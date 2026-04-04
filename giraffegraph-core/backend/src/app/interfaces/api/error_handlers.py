from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.application.errors import (
    ConflictError,
    ExternalServiceError,
    NotFoundError,
    RuleViolationError,
)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        NotFoundError,
        _json_handler(status.HTTP_404_NOT_FOUND),
    )
    app.add_exception_handler(
        ConflictError,
        _json_handler(status.HTTP_409_CONFLICT),
    )
    app.add_exception_handler(
        RuleViolationError,
        _json_handler(status.HTTP_422_UNPROCESSABLE_CONTENT),
    )
    app.add_exception_handler(
        ExternalServiceError,
        _json_handler(status.HTTP_502_BAD_GATEWAY),
    )


def _json_handler(
    status_code: int,
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc)},
        )

    return handler
