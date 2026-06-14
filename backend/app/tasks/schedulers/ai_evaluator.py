import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.database.base import get_db
from app.database.models.ai_memory import AIModel, Prediction
from app.database.models.market import Candle, MarketPair

logger = logging.getLogger(__name__)


def _latest_price_for_symbol(db: Session, symbol: str):
    pair = db.query(MarketPair).filter(MarketPair.symbol == symbol).first()
    if not pair:
        return None
    row = db.query(Candle).filter(Candle.market_pair_id == pair.id).order_by(Candle.open_time.desc()).first()
    if not row:
        return None
    return float(row.close)


def _evaluate_one(pred: Prediction, db: Session) -> None:
    actual_price = _latest_price_for_symbol(db, pred.symbol)
    if actual_price is None:
        return
    actual_direction = "BULLISH" if actual_price > 0 else "BEARISH"
    pred.actual_direction = actual_direction
    pred.is_correct = pred.predicted_direction == actual_direction
    db.add(pred)


def evaluate_predictions() -> None:
    db: Session | None = None
    try:
        db = next(get_db())
        cutoff = datetime.now(UTC) - timedelta(hours=1)
        rows = db.query(Prediction).filter(Prediction.created_at <= cutoff, Prediction.is_correct.is_(None)).all()
        for pred in rows:
            _evaluate_one(pred, db)
        db.commit()

        for pred in rows:
            if pred.is_correct is None or pred.model_id is None:
                continue
            model = db.query(AIModel).filter(AIModel.id == pred.model_id).first()
            if not model:
                continue
            acc = db.query(func.avg(Prediction.is_correct)).filter(Prediction.model_id == model.id, Prediction.is_correct.is_not(None)).scalar()
            model.accuracy_score = float(acc) if acc is not None else None
            db.add(model)
        db.commit()
    except Exception:
        if db is not None and db.in_transaction():
            db.rollback()
        logger.exception("ai_prediction_evaluation_failed")
    finally:
        if db is not None:
            db.close()
