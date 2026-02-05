"""Core proxy handler for LLM request forwarding."""

import json
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Any

from aegis.api.schemas import ChatCompletionRequest, ChatCompletionResponse
from aegis.config import LLMProvider, get_settings
from aegis.proxy.providers.base import BaseLLMProvider
from aegis.proxy.providers.openai import OpenAIProvider
from aegis.proxy.streaming import format_sse_done, format_sse_message
from aegis.telemetry.logger import get_logger

logger = get_logger()


class ProxyHandler:
    """
    Core proxy handler for forwarding requests to LLM providers.

    Handles both streaming and non-streaming requests, managing
    provider selection and response formatting.
    """

    def __init__(self):
        self._providers: dict[str, BaseLLMProvider] = {}
        self._settings = get_settings()

    def get_provider(self, provider_name: str | None = None) -> BaseLLMProvider:
        """Get or create a provider instance."""
        name = provider_name or self._settings.default_provider.value

        if name not in self._providers:
            if name == LLMProvider.OPENAI.value:
                self._providers[name] = OpenAIProvider()
            else:
                raise ValueError(f"Unknown provider: {name}")

        return self._providers[name]

    async def complete(
        self,
        request: ChatCompletionRequest,
        api_key: str | None,
        request_id: str,
    ) -> ChatCompletionResponse:
        """
        Forward a non-streaming completion request.

        Args:
            request: The chat completion request
            api_key: API key for the LLM provider
            request_id: Unique request identifier for logging

        Returns:
            Complete chat response from the LLM
        """
        provider = self.get_provider()

        logger.debug(
            "forwarding_request",
            request_id=request_id,
            provider=provider.name,
            model=request.model,
        )

        response = await provider.complete(request, api_key)

        logger.debug(
            "received_response",
            request_id=request_id,
            provider=provider.name,
            finish_reason=response.choices[0].finish_reason if response.choices else None,
        )

        return response

    async def stream_completion(
        self,
        request: ChatCompletionRequest,
        api_key: str | None,
        request_id: str,
    ) -> AsyncGenerator[str, None]:
        """
        Forward a streaming completion request.

        Args:
            request: The chat completion request
            api_key: API key for the LLM provider
            request_id: Unique request identifier for logging

        Yields:
            SSE-formatted string chunks for the response
        """
        provider = self.get_provider()

        logger.debug(
            "forwarding_stream_request",
            request_id=request_id,
            provider=provider.name,
            model=request.model,
        )

        chunk_count = 0
        try:
            async for chunk in provider.stream(request, api_key):
                chunk_count += 1
                yield format_sse_message(chunk)

            yield format_sse_done()

            logger.debug(
                "stream_completed",
                request_id=request_id,
                provider=provider.name,
                chunk_count=chunk_count,
            )
        except Exception as e:
            logger.error(
                "stream_error",
                request_id=request_id,
                provider=provider.name,
                error=str(e),
            )
            raise

    async def close(self) -> None:
        """Clean up all provider connections."""
        for provider in self._providers.values():
            await provider.close()
        self._providers.clear()


# Singleton instance
_proxy_handler: ProxyHandler | None = None


def get_proxy_handler() -> ProxyHandler:
    """Get the singleton proxy handler instance."""
    global _proxy_handler
    if _proxy_handler is None:
        _proxy_handler = ProxyHandler()
    return _proxy_handler
