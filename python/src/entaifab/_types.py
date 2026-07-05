"""Response objects with the same attribute access as the OpenAI Python SDK
(`response.choices[0].message.content`), built tolerantly from the gateway's
JSON so a missing optional field never raises."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class ChatCompletionMessage:
    role: str
    content: str

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionMessage":
        return cls(role=data.get("role", ""), content=data.get("content", ""))


@dataclass
class Choice:
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str]

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Choice":
        return cls(
            index=data.get("index", 0),
            message=ChatCompletionMessage._from_dict(data.get("message") or {}),
            finish_reason=data.get("finish_reason"),
        )


@dataclass
class CompletionUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "CompletionUsage":
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )


@dataclass
class ChatCompletion:
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[CompletionUsage]

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "ChatCompletion":
        usage = data.get("usage")
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion"),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=[Choice._from_dict(c) for c in data.get("choices") or []],
            usage=CompletionUsage._from_dict(usage) if usage else None,
        )


@dataclass
class Model:
    id: str
    object: str
    created: int
    owned_by: str

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Model":
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "model"),
            created=data.get("created", 0),
            owned_by=data.get("owned_by", "entaifab"),
        )


@dataclass
class ModelsPage:
    """Iterable list of models, matching `for m in client.models.list()`."""

    data: List[Model] = field(default_factory=list)
    object: str = "list"

    def __iter__(self) -> Iterator[Model]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    @classmethod
    def _from_dict(cls, payload: Dict[str, Any]) -> "ModelsPage":
        return cls(
            data=[Model._from_dict(m) for m in payload.get("data") or []],
            object=payload.get("object", "list"),
        )
