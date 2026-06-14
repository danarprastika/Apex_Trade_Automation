import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from datetime import timedelta

import pandas as pd
from sqlalchemy.orm import Session
from ta.momentum import RSIIndicator
from ta.trend import MACD
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

from app.core.config.settings import settings
from app.database.base import SessionLocal
from app.database.models.ai_memory import AIModel
from app.database.models.market import Candle, MarketPair


MODEL_PATH = BACKEND_DIR / "models" / "btc_rf_v1.joblib"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_candles(symbol: str = "BTCUSDT", limit: int = 5000):
    db: Session = SessionLocal()
    try:
        pair = db.query(MarketPair).filter(MarketPair.symbol == symbol).first()
        if not pair:
            raise SystemExit(f"Market pair not found: {symbol}")

        rows = (
            db.query(Candle)
            .filter(Candle.market_pair_id == pair.id)
            .order_by(Candle.open_time.asc())
            .limit(limit)
            .all()
        )
        if not rows:
            raise SystemExit("No candle data available")

        data = [
            {
                "timestamp": row.open_time,
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": float(row.volume),
            }
            for row in rows
        ]
        return pd.DataFrame(data)
    finally:
        db.close()


def build_features(df: pd.DataFrame):
    frame = df.copy()
    close = frame["close"].astype(float)

    frame["return_1"] = close.pct_change(1)
    frame["return_3"] = close.pct_change(3)
    frame["volatility"] = close.rolling(14).std() / (close.rolling(14).mean() + 1e-9)

    rsi = RSIIndicator(close=close, window=14).rsi()
    frame["rsi"] = rsi

    macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
    frame["macd"] = macd.macd()
    frame["macd_signal"] = macd.macd_signal()

    frame["target"] = (close.shift(-1) > close).astype(int)
    frame = frame.dropna().reset_index(drop=True)

    feature_cols = ["return_1", "return_3", "volatility", "rsi", "macd", "macd_signal"]
    X = frame[feature_cols].astype(float)
    y = frame["target"].astype(int)
    return frame, X, y, feature_cols


def train_and_save():
    df = load_candles("BTCUSDT", 5000)
    frame, X, y, feature_cols = build_features(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = float(accuracy_score(y_test, preds))

    joblib.dump(model, MODEL_PATH)

    db: Session = SessionLocal()
    try:
        existing = db.query(AIModel).filter(AIModel.name == "btc_rf_v1").first()
        if not existing:
            existing = AIModel(
                name="btc_rf_v1",
                version="v1",
                architecture="RandomForestClassifier",
                target_asset="BTCUSDT",
                accuracy_score=acc,
                is_active=True,
            )
            db.add(existing)
        else:
            existing.accuracy_score = acc
            existing.is_active = True
        db.commit()
        db.refresh(existing)
        print(f"Model saved to {MODEL_PATH}")
        print(f"Registered model id={existing.id}, accuracy={acc:.4f}")
    finally:
        db.close()


if __name__ == "__main__":
    train_and_save()
