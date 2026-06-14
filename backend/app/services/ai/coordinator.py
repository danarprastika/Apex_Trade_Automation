import logging
from datetime import UTC, datetime
from typing import Protocol

import pandas as pd
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.database.models.agents import AIAgent, AgentDecision, FinalDecision
from app.services.ai.agents.base_agent import BaseAgent
from app.services.ai.agents.market_agent import MarketAgent
from app.services.ai.agents.risk_agent import RiskAgent
from app.services.ai.agents.sentiment_agent import SentimentAgent

logger = logging.getLogger(__name__)

_AGENTS = [MarketAgent(), RiskAgent(), SentimentAgent()]


class AgentCoordinator:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_agents(self) -> None:
        for agent in _AGENTS:
            row = self.db.query(AIAgent).filter(AIAgent.name == agent.name).first()
            if not row:
                row = AIAgent(name=agent.name, role_type=agent.role_type, status="ACTIVE")
                self.db.add(row)
        self.db.commit()

    def _collect(self, symbol: str, df: pd.DataFrame) -> list[dict]:
        results: list[dict] = []
        for agent in _AGENTS:
            try:
                out = agent.analyze(symbol, df)
                if out:
                    out.setdefault("symbol", symbol)
                    results.append(out)
            except Exception as exc:
                logger.exception("agent_failed_graceful_degradation", agent=agent.name, symbol=symbol, error=str(exc))
        return results

    def _save_decisions(self, symbol: str, results: list[dict]) -> None:
        for item in results:
            row = AgentDecision(
                agent_name=item.get("agent"),
                symbol=item.get("symbol", symbol),
                decision=item.get("decision"),
                confidence=str(item.get("confidence")),
                reasoning_text=item.get("reasoning"),
            )
            self.db.add(row)
        self.db.commit()

    def _consensus(self, results: list[dict]) -> dict:
        if not results:
            return {"action": "HOLD", "score": "0.0"}
        actions = [item.get("decision") for item in results]
        best = max(set(actions), key=actions.count)
        score = round(sum(1 for a in actions if a == best) / len(actions), 2)
        return {"action": best, "score": str(score)}

    def _save_final(self, symbol: str, consensus: dict) -> None:
        final = FinalDecision(
            symbol=symbol,
            final_action=consensus.get("action", "HOLD"),
            consensus_score=consensus.get("score"),
        )
        self.db.add(final)
        self.db.commit()

    def run(self, symbol: str, df: pd.DataFrame) -> dict:
        self._ensure_agents()
        results = self._collect(symbol, df)
        self._save_decisions(symbol, results)
        consensus = self._consensus(results)
        self._save_final(symbol, consensus)
        return {"symbol": symbol, "agents": results, **consensus}


def run_multi_agent_decision(symbol: str, df: pd.DataFrame | None = None, limit: int = 64) -> dict | None:
    coordinator_db: Session | None = None
    if df is None:
        coordinator_db = next(get_db())
        try:
            from app.database.models.market import Candle, MarketPair
            pair = coordinator_db.query(MarketPair).filter(MarketPair.symbol == symbol).first()
            if not pair:
                return None
            rows = (
                coordinator_db.query(Candle)
                .filter(Candle.market_pair_id == pair.id)
                .order_by(Candle.open_time.desc())
                .limit(limit)
                .all()
            )
            if not rows:
                return None
            df = pd.DataFrame(
                [
                    {
                        "timestamp": row.open_time,
                        "open": float(row.open),
                        "high": float(row.high),
                        "low": float(row.low),
                        "close": float(row.close),
                        "volume": float(row.volume),
                    }
                    for row in reversed(rows)
                ]
            )
        finally:
            coordinator_db.close()

    coordinator = AgentCoordinator(db=next(get_db()))
    try:
        return coordinator.run(symbol, df)
    finally:
        coordinator.db.close()
