"""SSE streaming utilities for LLM responses."""

import json
from collections.abc import AsyncGenerator
from typing import Any


async def parse_sse_stream(
    response_stream: AsyncGenerator[bytes, None],
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Parse Server-Sent Events from an async byte stream.

    Yields parsed JSON objects from SSE data lines.
    """
    buffer = ""

    async for chunk in response_stream:
        buffer += chunk.decode("utf-8")

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()

            if not line:
                continue

            if line.startswith("data: "):
                data = line[6:]  # Strip "data: " prefix

                if data == "[DONE]":
                    return

                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    continue


def format_sse_message(data: dict[str, Any] | str) -> str:
    """Format a message for SSE transmission."""
    if isinstance(data, dict):
        data = json.dumps(data)
    return f"data: {data}\n\n"


def format_sse_done() -> str:
    """Format the SSE stream termination message."""
    return "data: [DONE]\n\n"
