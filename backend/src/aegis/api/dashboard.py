from fastapi import APIRouter, Depends
from aegis.telemetry.stats import get_stats_store, StatsStore

router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(store: StatsStore = Depends(get_stats_store)):
    return {
        "summary": store.get_stats(),
        "chart_data": store.get_chart_data()
    }


@router.get("/activity")
async def get_recent_activity(store: StatsStore = Depends(get_stats_store)):
    return {
        "recent_requests": store.get_activity()
    }
