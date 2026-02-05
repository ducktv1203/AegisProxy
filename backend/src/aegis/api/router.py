"""OpenAI-compatible API router."""

from aegis.telemetry.stats import get_stats_store, StatsStore, RequestRecord
from datetime import datetime
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from aegis.api.dependencies import ApiKey, ClientInfo, RequestId, SettingsDep
from aegis.api.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorDetail,
    SecurityBlockResponse,
)
from aegis.filters.pipeline import FilterPipeline, get_filter_pipeline
from aegis.proxy.handler import ProxyHandler, get_proxy_handler
from aegis.telemetry.logger import get_logger

router = APIRouter(prefix="/v1", tags=["OpenAI Compatible"])
logger = get_logger()


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    responses={
        403: {"model": SecurityBlockResponse, "description": "Request blocked by security policy"},
        502: {"description": "Upstream LLM provider error"},
    },
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    request_id: RequestId,
    api_key: ApiKey,
    client_info: ClientInfo,
    settings: SettingsDep,
    pipeline: FilterPipeline = Depends(get_filter_pipeline),
    proxy: ProxyHandler = Depends(get_proxy_handler),
    stats_store: StatsStore = Depends(get_stats_store),  # Inject stats store
):
    """
    Create a chat completion (OpenAI-compatible).

    This endpoint intercepts requests, runs them through the security filter
    pipeline, and forwards safe requests to the configured LLM provider.
    """
    start_time = time.time()

    # Log incoming request (no sensitive data)
    logger.info(
        "chat_completion_request",
        request_id=request_id,
        model=request.model,
        message_count=len(request.messages),
        stream=request.stream,
        **client_info,
    )

    # Run through security filter pipeline
    filter_result = await pipeline.process(
        messages=request.messages,
        request_id=request_id,
        client_info=client_info,
    )

    # Calculate metrics for stats
    pii_count = len(
        [f for f in filter_result.all_findings if f.type.value == "pii"])
    # Helper to safe-get injection score from metadata
    injection_score = 0.0
    for f in filter_result.all_findings:
        if f.type.value == "injection":
            injection_score = max(injection_score, f.confidence)

    # Handle blocked requests
    if filter_result.blocked:
        logger.warning(
            "request_blocked",
            request_id=request_id,
            reason=filter_result.block_reason,
            filter_name=filter_result.blocking_filter,
        )

        # Record blocked request
        stats_store.record_request(RequestRecord(
            id=request_id,
            timestamp=datetime.utcnow().isoformat(),
            status="blocked",
            pii_count=pii_count,
            injection_score=injection_score,
            latency_ms=(time.time() - start_time) * 1000,
            model=request.model
        ))

        raise HTTPException(
            status_code=403,
            detail=SecurityBlockResponse(
                error=ErrorDetail(
                    message=f"Request blocked by security policy: {filter_result.block_reason}",
                    type="security_block",
                    code="prompt_injection_detected",
                ),
                security_event_id=request_id,
            ).model_dump(),
        )

    # Use redacted messages for LLM call
    modified_request = request.model_copy(
        update={"messages": filter_result.processed_messages}
    )

    # Forward to LLM
    try:
        if request.stream:
            # Note: Streaming requests are hard to record "success" status for accurately
            # without wrapping the stream generator. For now, we record as allowed immediately.
            stats_store.record_request(RequestRecord(
                id=request_id,
                timestamp=datetime.utcnow().isoformat(),
                status="allowed",
                pii_count=pii_count,
                injection_score=injection_score,
                latency_ms=(time.time() - start_time) * 1000,
                model=request.model
            ))

            return StreamingResponse(
                proxy.stream_completion(modified_request, api_key, request_id),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Request-ID": request_id,
                },
            )
        else:
            response = await proxy.complete(modified_request, api_key, request_id)

            # Record allowed request (completed)
            stats_store.record_request(RequestRecord(
                id=request_id,
                timestamp=datetime.utcnow().isoformat(),
                status="allowed",
                pii_count=pii_count,
                injection_score=injection_score,
                latency_ms=(time.time() - start_time) * 1000,
                model=request.model
            ))

            return response
    except Exception as e:
        logger.error(
            "proxy_error",
            request_id=request_id,
            error=str(e),
        )
        # Record error
        stats_store.record_request(RequestRecord(
            id=request_id,
            timestamp=datetime.utcnow().isoformat(),
            status="error",
            pii_count=pii_count,
            injection_score=injection_score,
            latency_ms=(time.time() - start_time) * 1000,
            model=request.model
        ))

        raise HTTPException(
            status_code=502,
            detail={"message": "Error communicating with LLM provider",
                    "type": "proxy_error"},
        )


@router.get("/models")
async def list_models():
    """List available models (pass-through to provider)."""
    # Placeholder - will forward to actual provider
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai",
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai",
            },
        ],
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "version": "0.1.0",
    }
