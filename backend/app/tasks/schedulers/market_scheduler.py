import asyncio
import inspect
from collections.abc import Callable
from typing import Any

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.ai.coordinator import run_multi_agent_decision
from app.services.market.collector_service import fetch_and_store_candles
from app.tasks.schedulers.ai_evaluator import evaluate_predictions
from app.tasks.schedulers.self_learning import self_learning_scheduler

logger = structlog.get_logger(__name__)


class MarketScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self.scheduler.add_job(
            self._wrapped_job(fetch_and_store_candles),
            trigger=IntervalTrigger(minutes=1),
            id="market_candle_collector_1m",
            name="collect_btcusdt_1m",
            args=["BTC/USDT", "1m"],
            max_instances=1,
            coalesce=False,
            misfire_grace_time=None,
        )
        self.scheduler.add_job(
            self._wrapped_job(evaluate_predictions),
            trigger=IntervalTrigger(hours=1),
            id="ai_prediction_evaluator",
            name="evaluate_ai_predictions",
            max_instances=1,
            coalesce=False,
            misfire_grace_time=None,
        )
        self.scheduler.add_job(
            self._wrapped_job(self._evaluate_multi_agent_decisions),
            trigger=IntervalTrigger(minutes=5),
            id="multi_agent_decision_5m",
            name="evaluate_multi_agent_decisions",
            args=["BTC/USDT"],
            max_instances=1,
            coalesce=False,
            misfire_grace_time=None,
        )
        self_learning_scheduler.scheduler = self.scheduler
        self_learning_scheduler.register()
        self.scheduler.start()
        logger.info("market_scheduler_started", jobs=[job.name for job in self.scheduler.get_jobs()])

    async def _evaluate_multi_agent_decisions(self, symbol: str) -> None:
        await asyncio.to_thread(run_multi_agent_decision, symbol)

    def shutdown(self) -> None:
        if not self._running:
            return
        self._running = False
        self.scheduler.shutdown(wait=False)
        logger.info("market_scheduler_stopped")

    @staticmethod
    def _wrapped_job(func: Callable[..., Any]) -> Callable[..., Any]:
        async def _wrapper(*args: Any, **kwargs: Any) -> None:
            job_name = func.__name__
            logger.info("job_started", job=job_name, args=args, kwargs=kwargs)
            try:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:  # pragma: no cover - safety net
                logger.exception("job_failed", job=job_name, error=str(exc))
            else:
                logger.info("job_finished", job=job_name)

        return _wrapper


market_scheduler = MarketScheduler()
