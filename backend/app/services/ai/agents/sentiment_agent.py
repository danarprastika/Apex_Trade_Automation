from typing import Protocol

import pandas as pd

from app.services.ai.agents.base_agent import BaseAgent
from app.services.intelligence.sentiment_engine import SentimentAnalyzer


class SentimentAgent(BaseAgent):
    name = "sentiment_agent"
    role_type = "SENTIMENT"

    def analyze(self, symbol: str, df: pd.DataFrame) -> dict | None:
        if df is None or df.empty:
            return None
        analyzer = SentimentAnalyzer()
        latest = df.iloc[-1]
        text = f"{symbol} market update. Latest close {latest.get('close')}."
        result = analyzer.analyze(text)
        if not result:
            return None
        action = "HOLD"
        if result.get("sentiment") == "BULLISH":
            action = "BUY"
        elif result.get("sentiment") == "BEARISH":
            action = "SELL"
        return {
            "agent": self.name,
            "role": self.role_type,
            "symbol": symbol,
            "decision": action,
            "confidence": float(result.get("confidence_score", 0.5)),
            "reasoning": f"Sentiment {result.get('sentiment')}",
        }
