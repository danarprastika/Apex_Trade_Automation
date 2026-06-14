from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.rate_limit import INTERNAL_API_LIMIT, limiter
from app.database.base import get_db
from app.database.models.ai_memory import AIModel, Prediction


class ModelOut(BaseModel):
    id: str
    name: str
    version: str
    architecture: str
    target_asset: str
    accuracy_score: float | None
    is_active: bool

    class Config:
        from_attributes = True


class PredictionOut(BaseModel):
    id: str
    model_id: str
    symbol: str
    predicted_direction: str
    confidence_score: float
    actual_direction: str | None
    is_correct: bool | None
    created_at: str | None

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/models", response_model=list[ModelOut])
@limiter.limit(INTERNAL_API_LIMIT)
def list_ai_models(request: Request, db: Session = Depends(get_db)):
    rows = db.execute(select(AIModel).order_by(desc(AIModel.created_at))).scalars().all()
    return [
        ModelOut(
            id=str(row.id),
            name=row.name,
            version=row.version,
            architecture=row.architecture,
            target_asset=row.target_asset,
            accuracy_score=float(row.accuracy_score) if row.accuracy_score is not None else None,
            is_active=row.is_active,
        )
        for row in rows
    ]


@router.get("/predictions", response_model=list[PredictionOut])
@limiter.limit(INTERNAL_API_LIMIT)
def list_predictions(request: Request, db: Session = Depends(get_db)):
    rows = db.execute(select(Prediction).order_by(desc(Prediction.created_at)).limit(200)).scalars().all()
    return [
        PredictionOut(
            id=str(row.id),
            model_id=str(row.model_id),
            symbol=row.symbol,
            predicted_direction=row.predicted_direction,
            confidence_score=float(row.confidence_score),
            actual_direction=row.actual_direction,
            is_correct=row.is_correct,
            created_at=row.created_at.isoformat() if row.created_at else None,
        )
        for row in rows
    ]
