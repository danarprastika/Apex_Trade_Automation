from typing import Protocol

import pandas as pd
from ta.trend import EMAIndicator

from app.database.base import get_db
from app.database.models.market import Candle, MarketPair
from app.database.repositories.strategy_repository import create_signal, get_strategy_by_code


class BaseStrategy(Protocol):
    code: str
    name: str
    version: str
    strategy_type: str

    def evaluate(self, df: pd.DataFrame, pair_symbol: str) -> dict | None:
        ...


class EMACrossStrategy:
    code = "EMA_CROSS_V1"
    name = "EMA Cross Strategy"
    version = "1.0.0"
    strategy_type = "TREND_FOLLOWING"

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


class AIPredictionStrategy:
    code = "AI_PREDICTION_V1"
    name = "AI Prediction Strategy"
    version = "0.1.0"
    strategy_type = "AI_ML"

    def __init__(self, min_confidence: float = 0.75, model_name: str = "btc_rf_v1"):
        from app.services.ai.prediction_engine import MachineLearningEngine
        self.min_confidence = min_confidence
        self.engine = MachineLearningEngine()
        self.model_name = model_name

    def evaluate(self, df: pd.DataFrame, pair_symbol: str) -> dict | None:
        if df is None or df.empty or len(df) < 2:
            return None
        result = self.engine.predict_next_move(pair_symbol, df)
        if not result:
            return None
        if result.get("confidence_score", 0) < self.min_confidence:
            return None
        direction = result.get("predicted_direction")
        signal_type = "BUY" if direction == "BULLISH" else "SELL" if direction == "BEARISH" else None
        if not signal_type:
            return None
        return {
            "signal_type": signal_type,
            "reason": f"AI prediction: {direction} ({result.get('confidence_score')})",
            "entry_price": float(df["close"].iloc[-1]),
            "confidence": float(result.get("confidence_score", 0)) * 100,
        }


def _load_candles_as_df(symbol: str, timeframe: str = "1h", limit: int = 200) -> pd.DataFrame:
    db = next(get_db())
    try:
        pair = db.query(MarketPair).filter(MarketPair.symbol == symbol).first()
        if not pair:
            return pd.DataFrame()

        rows = (
            db.query(Candle)
            .filter(Candle.market_pair_id == pair.id, Candle.timeframe == timeframe)
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


def run_strategy(symbol: str, timeframe: str = "1h") -> None:
    db = next(get_db())
    try:
        strategy = get_strategy_by_code(db, EMACrossStrategy.code)
        if not strategy:
            return

        pair = db.query(MarketPair).filter(MarketPair.symbol == symbol).first()
        if not pair:
            return

        df = _load_candles_as_df(symbol, timeframe)
        if df.empty:
            return

        engine = EMACrossStrategy()
        result = engine.evaluate(df, symbol)
        if not result:
            return

        create_signal(
            db,
            strategy_id=strategy.id,
            market_pair_id=pair.id,
            signal_type=result["signal_type"],
            confidence=result.get("confidence"),
            entry_price=result.get("entry_price"),
            reason=result.get("reason"),
        )
    finally:
        db.close()


def run_strategy(symbol: str, timeframe: str = "1h") -> None:
    strategy_code = EMACrossStrategy.code
    db = next(get_db())
    try:
        strategy = get_strategy_by_code(db, strategy_code)
        if not strategy:
            return

        pair = db.query(MarketPair).filter(MarketPair.symbol == symbol).first()
        if not pair:
            return

        df = _load_candles_as_df(symbol, timeframe)
        if df.empty:
            return

        engine = EMACrossStrategy()
        result = engine.evaluate(df, symbol)
        if not result:
            return

        create_signal(
            db,
            strategy_id=strategy.id,
            market_pair_id=pair.id,
            signal_type=result["signal_type"],
            confidence=result.get("confidence"),
            entry_price=result.get("entry_price"),
            reason=result.get("reason"),
        )
    finally:
        db.close()
