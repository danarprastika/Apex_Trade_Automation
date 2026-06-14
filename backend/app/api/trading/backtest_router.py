from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.core.config.settings import settings
from app.database.base import get_db
from app.database.models.trading import Strategy
from app.database.models.backtest import BacktestRun
from app.services.trading.backtest_service import run_backtest


router = APIRouter()


class BacktestRunRequest(BaseModel):
    strategy_id: str
    start_date: datetime
    end_date: datetime
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"


class BacktestRunResponse(BaseModel):
    backtest_id: str
    total_trades: int | None
    win_rate: float | None
    profit_factor: float | None
    max_drawdown: float | None
    trades: list[dict[str, Any]] | None


class BacktestHistoryItem(BaseModel):
    id: str
    strategy_id: str
    start_date: datetime
    end_date: datetime
    profit_factor: float | None
    drawdown: float | None
    win_rate: float | None
    total_trades: int | None
    created_at: datetime | None


@router.post("/run", response_model=BacktestRunResponse)
def run_backtest_endpoint(payload: BacktestRunRequest, db: Session = Depends(get_db)):
    result = run_backtest(
        strategy_id=payload.strategy_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        symbol=payload.symbol,
        timeframe=payload.timeframe,
    )
    return BacktestRunResponse(
        backtest_id=result["backtest_id"],
        total_trades=result.get("total_trades"),
        win_rate=result.get("win_rate"),
        profit_factor=result.get("profit_factor"),
        max_drawdown=result.get("max_drawdown"),
        trades=result.get("trades"),
    )


@router.get("/results", response_model=list[BacktestHistoryItem])
def list_backtest_results(db: Session = Depends(get_db)):
    rows = db.execute(select(BacktestRun).order_by(desc(BacktestRun.created_at))).scalars().all()
    return [
        BacktestHistoryItem(
            id=str(row.id),
            strategy_id=str(row.strategy_id),
            start_date=row.start_date,
            end_date=row.end_date,
            profit_factor=float(row.profit_factor) if row.profit_factor is not None else None,
            drawdown=float(row.drawdown) if row.drawdown is not None else None,
            win_rate=float(row.win_rate) if row.win_rate is not None else None,
            total_trades=int(row.total_trades) if row.total_trades is not None else None,
            created_at=row.created_at,
        )
        for row in rows
    ]
