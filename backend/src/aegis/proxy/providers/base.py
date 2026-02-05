"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from aegis.api.schemas import ChatCompletionRequest, ChatCompletionResponse


class BaseLLMProvider(ABC):
    """Abstract base class for LLM provider implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass

    @abstractmethod
    async def complete(
        self,
        request: ChatCompletionRequest,
        api_key: str | None,
    ) -> ChatCompletionResponse:
        """
        Send a non-streaming completion request.

        Args:
            request: The chat completion request
            api_key: API key for authentication

        Returns:
            Complete chat response
        """
        pass

    @abstractmethod
    async def stream(
        self,
        request: ChatCompletionRequest,
        api_key: str | None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Send a streaming completion request.

        Args:
            request: The chat completion request
            api_key: API key for authentication

        Yields:
            Parsed SSE chunks from the response
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up provider resources."""
        pass
