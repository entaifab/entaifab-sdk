"""EntaiFab client - the same call shapes as the OpenAI Python SDK, pointed
at your organization's EntaiFab AI Gateway. Standard library only: no
runtime dependencies to audit or conflict with.

    from entaifab import EntaiFab

    client = EntaiFab(api_key="efab_...", organization_id="<org-guid>")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)

Each API key is bound to one provider + model in the EntaiFab dashboard, so
`model` is optional - omit it and the key's bound model is used. Pass it only
to override, and only with the provider's exact model id (e.g.
"gemini-2.5-flash"), never a route alias.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, Optional

from ._errors import APIConnectionError, EntaiFabError, status_error_class
from ._types import ChatCompletion, ModelsPage
from ._version import __version__

DEFAULT_API_HOST = "https://api.entaifab.com"
DEFAULT_TIMEOUT = 60.0


class Completions:
    def __init__(self, client: "EntaiFab") -> None:
        self._client = client

    def create(
        self,
        *,
        messages: Iterable[Dict[str, str]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **extra: Any,
    ) -> ChatCompletion:
        """Create a chat completion.

        Args:
            messages: OpenAI-style messages, e.g.
                [{"role": "user", "content": "Hello!"}].
            model: Optional override of the provider's exact model id (e.g.
                "gemini-2.5-flash") - never a route alias. Omit it and the
                API key's bound model is used; this is the normal path, and
                it means an admin can swap the provider/model behind your
                key later without you changing any code.
            provider: Deprecated, ignored by the gateway. Routing is fully
                determined by the API key now, so there's nothing left to
                disambiguate. Kept only so older code that still passes it
                doesn't break.
            temperature: Optional sampling temperature.
            max_tokens: Optional completion token cap.
            extra: Forward-compatible passthrough of additional fields.
        """
        body: Dict[str, Any] = {"messages": list(messages)}
        if model is not None:
            body["model"] = model
        if provider is not None:
            body["provider"] = provider
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        body.update(extra)
        payload = self._client._request("POST", "/chat/completions", body)
        return ChatCompletion._from_dict(payload)


class Chat:
    def __init__(self, client: "EntaiFab") -> None:
        self.completions = Completions(client)


class Models:
    def __init__(self, client: "EntaiFab") -> None:
        self._client = client

    def list(self) -> ModelsPage:
        """List the model this API key is bound to (empty if the key has no
        route assigned yet)."""
        return ModelsPage._from_dict(self._client._request("GET", "/models"))


class EntaiFab:
    """Client for the EntaiFab AI Gateway.

    Args:
        api_key: Gateway API key ("efab_..."). Falls back to the
            ENTAIFAB_API_KEY environment variable.
        organization_id: Your organization id (shown on the EntaiFab
            Developer Tools page). Falls back to ENTAIFAB_ORGANIZATION_ID.
        base_url: Full gateway base URL, e.g.
            "https://api.entaifab.com/gateway/<org-guid>/v1". Overrides
            organization_id when given. Falls back to ENTAIFAB_BASE_URL.
        timeout: Per-request timeout in seconds (default 60).
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        organization_id: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_key = api_key or os.environ.get("ENTAIFAB_API_KEY")
        if not self.api_key:
            raise EntaiFabError(
                "No API key provided. Pass api_key=... or set the ENTAIFAB_API_KEY environment variable."
            )

        base_url = base_url or os.environ.get("ENTAIFAB_BASE_URL")
        organization_id = organization_id or os.environ.get("ENTAIFAB_ORGANIZATION_ID")

        if base_url:
            self.base_url = base_url.rstrip("/")
        elif organization_id:
            self.base_url = f"{DEFAULT_API_HOST}/gateway/{organization_id}/v1"
        else:
            raise EntaiFabError(
                "No gateway endpoint configured. Pass organization_id=... (or base_url=...), "
                "or set the ENTAIFAB_ORGANIZATION_ID environment variable."
            )

        self.timeout = timeout
        self.chat = Chat(self)
        self.models = Models(self)

    def _request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode("utf-8") if body is not None else None,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"entaifab-python/{__version__}",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise self._status_error(exc) from None
        except urllib.error.URLError as exc:
            raise APIConnectionError(f"Could not reach the EntaiFab gateway: {exc.reason}") from exc

    @staticmethod
    def _status_error(exc: urllib.error.HTTPError) -> Exception:
        message = f"HTTP {exc.code}"
        code = None
        error_type = None
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("error") or {}
            message = detail.get("message", message)
            code = detail.get("code")
            error_type = detail.get("type")
        except Exception:
            pass
        return status_error_class(exc.code)(message, status_code=exc.code, code=code, type=error_type)
