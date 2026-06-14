from abc import ABC, abstractmethod
from typing import Protocol

import pandas as pd

from app.database.models.agents import DecisionAction


class BaseAgent(ABC):
    name: str
    role_type: str

    @abstractmethod
    def analyze(self, symbol: str, df: pd.DataFrame) -> dict | None:
        ...

    def _decision(self, action: DecisionAction, confidence: float, reasoning: str) -> dict:
        return {
            "agent": self.name,
            "role": self.role_type,
            "symbol": symbol if "symbol" in self._decision.__code__.co_varnames else symbol,
        }
