import time
from functools import wraps
from typing import Any, Callable

from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter('http_requests_total', 'Total HTTP Requests')
TOTAL_MESSAGES_PRODUCED = Counter(
    'messages_produced_to_ai_service_total',
    'Total messages produced to AI service'
)

CREATE_TASK_METHOD_DURATION = Histogram(
    'create_task_duration_seconds',
    'Time spent in creating task',
)
GET_ALL_TASKS_METHOD_DURATION = Histogram(
    'get_all_tasks_duration_seconds',
    'Measure time of getting all tasks from database and cache',
)


def measure_latency(histogram: Histogram) -> Callable[[Any], Any]:
    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.monotonic()
            result = await func(*args, **kwargs)
            duration = time.monotonic() - start_time
            histogram.observe(duration)
            return result

        return wrapper
    return decorator
