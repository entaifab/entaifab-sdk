"""Exception hierarchy, named to match the OpenAI Python SDK so migrating
code only has to change the import - `except openai.AuthenticationError`
becomes `except entaifab.AuthenticationError`."""

from __future__ import annotations

from typing import Optional


class EntaiFabError(Exception):
    """Base class for every error raised by this SDK."""


class APIConnectionError(EntaiFabError):
    """The request never reached the EntaiFab gateway (network failure,
    DNS error, timeout)."""

    def __init__(self, message: str = "Connection error.") -> None:
        super().__init__(message)


class APIStatusError(EntaiFabError):
    """The gateway responded with a non-success HTTP status.

    Attributes:
        status_code: HTTP status of the response.
        code: EntaiFab error code, e.g. "INVALID_API_KEY".
        type: OpenAI-style error type, e.g. "invalid_request_error".
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: Optional[str] = None,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.type = type


class BadRequestError(APIStatusError):
    """HTTP 400."""


class AuthenticationError(APIStatusError):
    """HTTP 401 - the API key is missing, invalid, revoked, or belongs to a
    different organization than the gateway URL."""


class PermissionDeniedError(APIStatusError):
    """HTTP 403."""


class NotFoundError(APIStatusError):
    """HTTP 404."""


class ConflictError(APIStatusError):
    """HTTP 409."""


class RateLimitError(APIStatusError):
    """HTTP 429."""


class InternalServerError(APIStatusError):
    """HTTP 5xx - includes 502, which the gateway returns when the upstream
    AI provider fails."""


_STATUS_ERROR_CLASSES = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


def status_error_class(status_code: int) -> type:
    if status_code >= 500:
        return InternalServerError
    return _STATUS_ERROR_CLASSES.get(status_code, APIStatusError)
