from collections.abc import Callable, Coroutine
from typing import Any

import structlog
from apscheduler.triggers.cron import CronTrigger

from app.services.ai.digital_twin import DigitalTwinEngine

logger = structlog.get_logger(__name__)


def _build_self_learning_job(coro_func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
    async def _wrapper(*args: Any, **kwargs: Any) -> None:
        job_name = coro_func.__name__
        logger.info("job_started", job=job_name, args=args, kwargs=kwargs)
        try:
            await coro_func(*args, **kwargs)
        except Exception as exc:
            logger.exception("job_failed", job=job_name, error=str(exc))
        else:
            logger.info("job_finished", job=job_name)
    return _wrapper


class SelfLearningScheduler:
    def __init__(self, scheduler) -> None:
        self.scheduler = scheduler
        self.engine = DigitalTwinEngine()

    def register(self) -> None:
        if self.scheduler is None:
            return
        self.scheduler.add_job(
            _build_self_learning_job(self._run_daily_assessment),
            trigger=CronTrigger(hour=0, minute=0),
            id="self_learning_daily",
            name="self_learning_daily_assessment",
            max_instances=1,
            coalesce=False,
            misfire_grace_time=None,
        )

    async def _run_daily_assessment(self) -> None:
        result = self.engine.simulate_alternative_scenarios("BTCUSDT")
        logger.info("self_learning_daily_assessment", result=result)


self_learning_scheduler = SelfLearningScheduler(None)
