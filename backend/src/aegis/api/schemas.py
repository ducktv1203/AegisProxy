"""OpenAI-compatible API request/response schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: Literal["system", "user", "assistant", "tool"] = Field(
        description="The role of the message author"
    )
    content: str | None = Field(
        default=None, description="The content of the message")
    name: str | None = Field(
        default=None, description="Optional name for the participant")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""

    model: str = Field(description="ID of the model to use")
    messages: list[ChatMessage] = Field(
        description="List of messages in the conversation")
    temperature: float | None = Field(default=1.0, ge=0.0, le=2.0)
    top_p: float | None = Field(default=1.0, ge=0.0, le=1.0)
    n: int | None = Field(default=1, ge=1, le=128)
    stream: bool = Field(
        default=False, description="Whether to stream responses")
    stop: str | list[str] | None = Field(default=None)
    max_tokens: int | None = Field(default=None, ge=1)
    presence_penalty: float | None = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float | None = Field(default=0.0, ge=-2.0, le=2.0)
    user: str | None = Field(
        default=None, description="Unique user identifier")


class ChatCompletionChoice(BaseModel):
    """A single completion choice."""

    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length",
                           "content_filter", "tool_calls"] | None = None


class Usage(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""

    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: Usage | None = None


# Streaming response models
class DeltaMessage(BaseModel):
    """Delta content for streaming responses."""

    role: Literal["assistant"] | None = None
    content: str | None = None


class StreamChoice(BaseModel):
    """A single streaming choice."""

    index: int
    delta: DeltaMessage
    finish_reason: Literal["stop", "length",
                           "content_filter", "tool_calls"] | None = None


class ChatCompletionChunk(BaseModel):
    """OpenAI-compatible streaming chunk."""

    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[StreamChoice]


# Error responses
class ErrorDetail(BaseModel):
    """Error detail following OpenAI format."""

    message: str
    type: str
    param: str | None = None
    code: str | None = None


class ErrorResponse(BaseModel):
    """OpenAI-compatible error response."""

    error: ErrorDetail


# Security-specific responses
class SecurityBlockResponse(BaseModel):
    """Response when a request is blocked by security filters."""

    error: ErrorDetail
    security_event_id: str | None = Field(
        default=None, description="Reference ID for the security event"
    )
