"""
In-memory statistics store for the dashboard.
In a real production app, this would be a database (Redis/Postgres).
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class RequestRecord:
    id: str
    timestamp: str
    status: Literal["allowed", "blocked", "error"]
    pii_count: int
    injection_score: float
    latency_ms: float
    model: str


@dataclass
class DashboardStats:
    total_requests: int = 0
    blocked_requests: int = 0
    pii_detected: int = 0
    injection_detected: int = 0
    start_time: str = field(
        default_factory=lambda: datetime.utcnow().isoformat())

# Singleton store


class StatsStore:
    def __init__(self):
        self.stats = DashboardStats()
        self.recent_requests: deque[RequestRecord] = deque(
            maxlen=100)  # Keep last 100 requests
        # "YYYY-MM-DD HH": {"total": 0, "blocked": 0}
        self.hourly_activity: dict[str, dict] = {}

    def record_request(self, record: RequestRecord):
        # Update counters
        self.stats.total_requests += 1
        if record.status == "blocked":
            self.stats.blocked_requests += 1
        if record.pii_count > 0:
            self.stats.pii_detected += record.pii_count
        if record.injection_score > 0.7:  # Threshold
            self.stats.injection_detected += 1

        # Add to history
        self.recent_requests.appendleft(record)

        # Update hourly activity (for chart)
        # Assuming timestamp is ISO format, gets the hour part
        hour_key = record.timestamp[:13]  # "2023-10-27T10"
        if hour_key not in self.hourly_activity:
            self.hourly_activity[hour_key] = {"total": 0, "blocked": 0}

        self.hourly_activity[hour_key]["total"] += 1
        if record.status == "blocked":
            self.hourly_activity[hour_key]["blocked"] += 1

    def get_stats(self):
        return self.stats

    def get_activity(self):
        return list(self.recent_requests)

    def get_chart_data(self):
        # Convert dict to sorted list for charts
        data = []
        for key in sorted(self.hourly_activity.keys())[-12:]:  # Last 12 hours
            time_label = key.split("T")[1] + ":00"
            data.append({
                "time": time_label,
                "requests": self.hourly_activity[key]["total"],
                "blocked": self.hourly_activity[key]["blocked"]
            })
        return data


# Global instance
_store = StatsStore()


def get_stats_store() -> StatsStore:
    return _store
