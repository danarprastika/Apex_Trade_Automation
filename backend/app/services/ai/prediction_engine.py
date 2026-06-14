import os
from datetime import UTC, datetime
from typing import Protocol

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.database.base import get_db
from app.database.models.ai_memory import AIModel, Prediction
from app.database.models.market import Candle, MarketPair


class BaseMLModel(Protocol):
    def predict(self, X):
        ...


class MachineLearningEngine:
    def __init__(self, model_dir: str | None = None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), "..", "..", "models")
        self._models: dict[str, BaseMLModel] = {}

    def load_model(self, model_name: str) -> BaseMLModel | None:
        if model_name in self._models:
            return self._models[model_name]
        path = os.path.join(self.model_dir, f"{model_name}.joblib")
        if not os.path.exists(path):
            return None
        try:
            import joblib
            model = joblib.load(path)
            self._models[model_name] = model
            return model
        except Exception:
            return None

    @staticmethod
    def _direction_from_return(ret: float) -> str:
        if ret > 0:
            return "BULLISH"
        if ret < 0:
            return "BEARISH"
        return "NEUTRAL"

    def predict_next_move(self, symbol: str, recent_candles: pd.DataFrame) -> dict | None:
        if recent_candles is None or recent_candles.empty:
            return None
        closes = recent_candles["close"].astype(float)
        if len(closes) < 2:
            return None
        future_return = float(closes.iloc[-1]) - float(closes.iloc[0])
        direction = self._direction_from_return(future_return)
        confidence = min(1.0, abs(future_return) / (float(closes.iloc[0]) + 1e-9))
        return {
            "symbol": symbol,
            "predicted_direction": direction,
            "confidence_score": round(float(confidence), 4),
            "predicted_at": datetime.now(UTC).isoformat(),
        }


def _recent_candles_df(symbol: str, limit: int = 64) -> pd.DataFrame:
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


def predict_and_store(symbol: str, model_name: str = "baseline_v1") -> dict | None:
    df = _recent_candles_df(symbol)
    engine = MachineLearningEngine()
    result = engine.predict_next_move(symbol, df)
    if not result:
        return None
    db: Session = next(get_db())
    try:
        model = db.query(AIModel).filter(AIModel.name == model_name).first()
        if not model:
            model = AIModel(
                name=model_name,
                version="0.1.0",
                architecture="rule-based-baseline",
                target_asset=symbol,
                accuracy_score=None,
            )
            db.add(model)
            db.commit()
            db.refresh(model)
        pred = Prediction(
            model_id=model.id,
            symbol=symbol,
            predicted_direction=result["predicted_direction"],
            confidence_score=result["confidence_score"],
        )
        db.add(pred)
        db.commit()
        db.refresh(pred)
        result["prediction_id"] = str(pred.id)
        result["model_id"] = str(model.id)
        return result
    finally:
        db.close()
