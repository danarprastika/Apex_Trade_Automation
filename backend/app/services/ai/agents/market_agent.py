from typing import Protocol

import pandas as pd

from app.services.ai.agents.base_agent import BaseAgent


class MarketAgent(BaseAgent):
    name = "market_agent"
    role_type = "MARKET"

    def analyze(self, symbol: str, df: pd.DataFrame) -> dict | None:
        if df is None or df.empty or len(df) < 20:
            return None
        close = df["close"].astype(float)
        ma = close.rolling(20).mean().iloc[-1]
        price = float(close.iloc[-1])
        confidence = 0.6
        action = "HOLD"
        if price > ma:
            action = "BUY"
            confidence = 0.7
        elif price < ma:
            action = "SELL"
            confidence = 0.7
        return {
            "agent": self.name,
            "role": self.role_type,
            "symbol": symbol,
            "decision": action,
            "confidence": confidence,
            "reasoning": f"Price {price} vs SMA20 {ma:.2f}",
        }
