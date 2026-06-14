from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.database.models.portfolio import PortfolioSnapshot
from app.services.portfolio.portfolio_service import get_latest_snapshot, PortfolioService

router = APIRouter()


class PortfolioOut(BaseModel):
    id: str
    total_balance_usdt: float
    asset_allocation: str | None
    created_at: str | None

    class Config:
        from_attributes = True


class SnapshotRequest(BaseModel):
    user_id: str | None = None


@router.get("/latest", response_model=PortfolioOut | None)
def latest_portfolio(db: Session = Depends(get_db)):
    row = db.execute(select(PortfolioSnapshot).order_by(desc(PortfolioSnapshot.created_at)).limit(1)).scalar_one_or_none()
    if not row:
        return None
    return PortfolioOut(
        id=str(row.id),
        total_balance_usdt=float(row.total_balance_usdt),
        asset_allocation=row.asset_allocation,
        created_at=row.created_at.isoformat() if row.created_at else None,
    )


@router.post("/snapshot")
def create_snapshot(payload: SnapshotRequest = SnapshotRequest(), db: Session = Depends(get_db)):
    service = PortfolioService()
    try:
        snapshot = service.snapshot_user_balance(payload.user_id)
        return {"success": True, "data": {"id": str(snapshot.id), "total_balance_usdt": float(snapshot.total_balance_usdt)}}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
