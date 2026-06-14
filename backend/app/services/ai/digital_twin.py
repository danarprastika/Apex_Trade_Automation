import json
from datetime import UTC, datetime
from typing import Literal

import pandas as pd
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.database.models.digital_twin import DigitalTwinRun, TwinScenarioType
from app.database.models.market import Candle, MarketPair


ScenarioName = Literal["AGGRESSIVE", "MODERATE", "CONSERVATIVE"]


def _load_candles_df(symbol: str, limit: int = 200) -> pd.DataFrame:
    db = next(get_db())
    try:
        pair = db.query(MarketPair).filter(MarketPair.symbol == symbol).first()
        if not pair:
            return pd.DataFrame()
        rows = (
            db.query(Candle)
            .filter(Candle.market_pair_id == pair.id)
            .order_by(Candle.open_time.desc())
            .limit(limit)
            .all()
        )
        if not rows:
            return pd.DataFrame()
        data = [
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
        return pd.DataFrame(data)
    finally:
        db.close()


def _simulate(df: pd.DataFrame, scenario: ScenarioName) -> dict:
    if df.empty or len(df) < 2:
        return {"pnl": 0.0, "drawdown": 0.0}
    closes = df["close"].astype(float).values
    position = 0
    entry = 0.0
    equity = 10_000.0
    peak = equity
    max_dd = 0.0

    if scenario == "AGGRESSIVE":
        threshold = 0.005
        size = 1.0
    elif scenario == "MODERATE":
        threshold = 0.01
        size = 0.5
    else:
        threshold = 0.015
        size = 0.25

    for i in range(1, len(closes)):
        ret = closes[i] - closes[i - 1] / (closes[i - 1] + 1e-9)
        if position == 0:
            if ret > threshold:
                position = 1
                entry = closes[i]
            elif ret < -threshold:
                position = -1
                entry = closes[i]
        else:
            if position == 1 and ret < -threshold:
                pnl = (closes[i] - entry) * size
                equity += pnl
                position = 0
            elif position == -1 and ret > threshold:
                pnl = (entry - closes[i]) * size
                equity += pnl
                position = 0
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd

    return {"pnl": round(equity - 10_000.0, 2), "drawdown": round(max_dd, 4)}


class DigitalTwinEngine:
    def simulate_alternative_scenarios(self, symbol: str = "BTCUSDT") -> dict:
        df = _load_candles_df(symbol)
        if df.empty:
            return {"symbol": symbol, "scenarios": {}}
        scenarios = {}
        for scenario in ["AGGRESSIVE", "MODERATE", "CONSERVATIVE"]:
            scenarios[scenario] = _simulate(df, scenario)
        db: Session = next(get_db())
        try:
            for name, result in scenarios.items():
                run = DigitalTwinRun(
                    symbol=symbol,
                    scenario_type=name,
                    simulated_pnl=result.get("pnl"),
                    simulated_drawdown=result.get("drawdown"),
                    parameters={"size": 1.0 if name == "AGGRESSIVE" else 0.5 if name == "MODERATE" else 0.25},
                )
                db.add(run)
            db.commit()
        finally:
            db.close()
        return {"symbol": symbol, "scenarios": scenarios}
