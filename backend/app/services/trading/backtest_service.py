from collections import deque
from datetime import datetime
from typing import Protocol

import pandas as pd
from ta.trend import EMAIndicator

from app.core.config.settings import settings
from app.database.base import get_db
from app.database.models.market import Candle, MarketPair
from app.database.models.trading import Strategy
from app.database.repositories.backtest_repository import create_backtest_run


class BaseStrategy(Protocol):
    evaluate(self, df: pd.DataFrame, pair_symbol: str) -> dict | None:
        ...


class EMACrossStrategy:
    code = "EMA_CROSS_V1"
    name = "EMA Cross Strategy"

    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        self.fast_period = fast_period
        self.slow_period = slow_period

    def evaluate(self, df: pd.DataFrame, pair_symbol: str) -> dict | None:
        if len(df) < self.slow_period + 1:
            return None

        ema_fast = EMAIndicator(close=df["close"], window=self.fast_period).ema_indicator()
        ema_slow = EMAIndicator(close=df["close"], window=self.slow_period).ema_indicator()

        prev_fast = ema_fast.iloc[-2]
        curr_fast = ema_fast.iloc[-1]
        prev_slow = ema_slow.iloc[-2]
        curr_slow = ema_slow.iloc[-1]

        signal_type = None
        reason = None

        if prev_fast <= prev_slow and curr_fast > curr_slow:
            signal_type = "BUY"
            reason = f"EMA{self.fast_period} crossed above EMA{self.slow_period}"
        elif prev_fast >= prev_slow and curr_fast < curr_slow:
            signal_type = "SELL"
            reason = f"EMA{self.slow_period} crossed below EMA{self.fast_period}"

        if not signal_type:
            return None

        return {
            "signal_type": signal_type,
            "reason": reason,
            "entry_price": float(df["close"].iloc[-1]),
            "confidence": 70.0,
        }


def _get_pair(db: Session, symbol: str) -> MarketPair | None:
    return db.query(MarketPair).filter(MarketPair.symbol == symbol).first()


def _load_candles_in_range(db: Session, pair_id, start_date, end_date, timeframe: str = "1h"):
    return (
        db.query(Candle)
        .filter(
            Candle.market_pair_id == pair_id,
            Candle.timeframe == timeframe,
            Candle.open_time >= start_date,
            Candle.open_time <= end_date,
        )
        .order_by(Candle.open_time.asc())
        .all()
    )


def run_backtest(strategy_id, start_date: datetime, end_date: datetime, symbol: str = "BTCUSDT", timeframe: str = "1h") -> dict:
    db = next(get_db())
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise ValueError("Strategy not found")

        pair = _get_pair(db, symbol)
        if not pair:
            raise ValueError("Market pair not found")

        rows = _load_candles_in_range(db, pair.id, start_date, end_date, timeframe)
        if not rows:
            raise ValueError("No candles in range")

        engine = EMACrossStrategy()
        window = deque(maxlen=engine.slow_period + 2)
        trades: list[dict] = []
        position: str | None = None
        entry_price: float | None = None

        for row in rows:
            window.append(
                {
                    "timestamp": row.open_time,
                    "open": float(row.open),
                    "high": float(row.high),
                    "low": float(row.low),
                    "close": float(row.close),
                    "volume": float(row.volume),
                }
            )

            if len(window) < engine.slow_period + 1:
                continue

            df = pd.DataFrame(list(window))
            result = engine.evaluate(df, symbol)
            if not result:
                continue

            signal = result["signal_type"]
            price = float(row.close)

            if position is None:
                if signal == "BUY":
                    position = "LONG"
                    entry_price = price
                elif signal == "SELL":
                    position = "SHORT"
                    entry_price = price
            elif position == "LONG":
                if signal == "SELL" and entry_price is not None:
                    pnl = price - entry_price
                    trades.append({"side": "LONG", "entry": entry_price, "exit": price, "pnl": pnl})
                    position = None
                    entry_price = None
            elif position == "SHORT":
                if signal == "BUY" and entry_price is not None:
                    pnl = entry_price - price
                    trades.append({"side": "SHORT", "entry": entry_price, "exit": price, "pnl": pnl})
                    position = None
                    entry_price = None

        pnl_list = [trade["pnl"] for trade in trades]
        gross_profit = sum(p for p in pnl_list if p > 0)
        gross_loss = abs(sum(p for p in pnl_list if p < 0))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (None if not gross_profit else float("inf"))
        win_rate = (sum(1 for p in pnl_list if p > 0) / len(pnl_list)) * 100 if pnl_list else None

        equity = 10000.0
        peak = equity
        max_drawdown = 0.0
        for p in pnl_list:
            equity += p
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0.0
            if dd > max_drawdown:
                max_drawdown = dd

        max_drawdown_pct = max_drawdown * 100 if max_drawdown else None

        backtest = create_backtest_run(
            db,
            strategy_id=strategy_id,
            start_date=start_date,
            end_date=end_date,
            profit_factor=profit_factor,
            drawdown=max_drawdown_pct,
            win_rate=win_rate,
            total_trades=len(trades),
        )

        return {
            "backtest_id": str(backtest.id),
            "total_trades": len(trades),
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown_pct,
            "trades": trades,
        }
    finally:
        db.close()
