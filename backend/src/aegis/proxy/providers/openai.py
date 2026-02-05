"""OpenAI API provider implementation."""

import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from aegis.api.schemas import ChatCompletionRequest, ChatCompletionResponse
from aegis.config import get_settings
from aegis.proxy.providers.base import BaseLLMProvider
from aegis.proxy.streaming import parse_sse_stream


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation."""

    def __init__(self, base_url: str | None = None, timeout: float = 60.0):
        settings = get_settings()
        self.base_url = base_url or settings.openai_base_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def name(self) -> str:
        return "openai"

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialize the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout, connect=10.0),
            )
        return self._client

    def _get_headers(self, api_key: str | None) -> dict[str, str]:
        """Build request headers."""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    async def complete(
        self,
        request: ChatCompletionRequest,
        api_key: str | None,
    ) -> ChatCompletionResponse:
        """Send a non-streaming completion request to OpenAI."""
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = False

        response = await self.client.post(
            "/chat/completions",
            headers=self._get_headers(api_key),
            json=payload,
        )
        response.raise_for_status()

        return ChatCompletionResponse.model_validate(response.json())

    async def stream(
        self,
        request: ChatCompletionRequest,
        api_key: str | None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Send a streaming completion request to OpenAI."""
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = True

        async with self.client.stream(
            "POST",
            "/chat/completions",
            headers=self._get_headers(api_key),
            json=payload,
        ) as response:
            response.raise_for_status()

            async for chunk in parse_sse_stream(response.aiter_bytes()):
                yield chunk

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
