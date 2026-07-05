"""Official Python SDK for the EntaiFab AI Gateway."""

from ._client import EntaiFab
from ._errors import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    EntaiFabError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)
from ._types import (
    ChatCompletion,
    ChatCompletionMessage,
    Choice,
    CompletionUsage,
    Model,
    ModelsPage,
)
from ._version import __version__

__all__ = [
    "EntaiFab",
    "EntaiFabError",
    "APIConnectionError",
    "APIStatusError",
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "InternalServerError",
    "ChatCompletion",
    "ChatCompletionMessage",
    "Choice",
    "CompletionUsage",
    "Model",
    "ModelsPage",
    "__version__",
]
