import uuid
from datetime import datetime
from typing import Protocol

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.database.base import get_db
from app.database.models.market import Candle, MarketPair
from app.database.models.portfolio import PortfolioSnapshot


class BasePortfolioService(Protocol):
    def snapshot_user_balance(self, user_id) -> PortfolioSnapshot:
        ...


class PortfolioService:
    def __init__(self) -> None:
        self.binance = None

    def _get_exchange(self):
        if self.binance is None:
            import ccxt
            api_key = getattr(settings, "BINANCE_API_KEY", "")
            api_secret = getattr(settings, "BINANCE_API_SECRET", "")
            self.binance = ccxt.binance({
                "apiKey": api_key,
                "secret": api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
            })
        return self.binance

    def snapshot_user_balance(self, user_id) -> PortfolioSnapshot:
        exchange = self._get_exchange()
        balance = exchange.fetch_balance()
        total = balance.get("total", {})
        btc_amount = float(total.get("BTC", 0) or 0)
        usdt_amount = float(total.get("USDT", 0) or 0)
        ticker = exchange.fetch_ticker("BTC/USDT")
        btc_price = float(ticker.get("last", 0) or 0)
        total_usdt = usdt_amount + btc_amount * btc_price

        db: Session = next(get_db())
        try:
            snapshot = PortfolioSnapshot(
                user_id=user_id,
                total_balance_usdt=total_usdt,
                asset_allocation=f'{{"BTC": {btc_amount}, "USDT": {usdt_amount}}}',
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
            return snapshot
        finally:
            db.close()


def get_latest_snapshot(user_id):
    db: Session = next(get_db())
    try:
        row = db.query(PortfolioSnapshot).filter(PortfolioSnapshot.user_id == user_id).order_by(PortfolioSnapshot.created_at.desc()).first()
        return row
    finally:
        db.close()
