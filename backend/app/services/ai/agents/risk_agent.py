from typing import Protocol

import pandas as pd

from app.services.ai.agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):
    name = "risk_agent"
    role_type = "RISK"

    def analyze(self, symbol: str, df: pd.DataFrame) -> dict | None:
        if df is None or df.empty or len(df) < 14:
            return None
        close = df["close"].astype(float)
        volatility = float(close.pct_change().abs().rolling(14).mean().iloc[-1])
        confidence = min(1.0, max(0.3, 1 - volatility * 100))
        action = "HOLD"
        if volatility > 0.05:
            action = "REDUCE_EXPOSURE"
        elif volatility < 0.015:
            action = "HOLD"
        return {
            "agent": self.name,
            "role": self.role_type,
            "symbol": symbol,
            "decision": action,
            "confidence": round(float(confidence), 2),
            "reasoning": f"14-period volatility={volatility:.4f}",
        }
