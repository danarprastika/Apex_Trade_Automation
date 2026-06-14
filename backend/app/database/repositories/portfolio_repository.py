import uuid
from datetime import datetime
from typing import Protocol

from sqlalchemy.orm import Session

from app.database.models.portfolio import PortfolioSnapshot


class BasePortfolioRepository(Protocol):
    def create_snapshot(self, db: Session, user_id, total_balance_usdt, asset_allocation=None) -> PortfolioSnapshot:
        ...


def create_snapshot(db: Session, user_id, total_balance_usdt, asset_allocation=None) -> PortfolioSnapshot:
    snapshot = PortfolioSnapshot(
        user_id=user_id,
        total_balance_usdt=total_balance_usdt,
        asset_allocation=asset_allocation,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot
