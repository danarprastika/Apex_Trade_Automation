from sqlalchemy.orm import Session

from app.database.models.trading import Signal, Strategy


def get_strategy_by_code(db: Session, code: str) -> Strategy | None:
    return db.query(Strategy).filter(Strategy.code == code, Strategy.status == "ACTIVE").first()


def create_signal(
    db: Session,
    strategy_id,
    market_pair_id,
    signal_type: str,
    confidence: float | None = None,
    entry_price: float | None = None,
    stop_loss: float | None = None,
    take_profit: float | None = None,
    reason: str | None = None,
) -> Signal:
    signal = Signal(
        strategy_id=strategy_id,
        market_pair_id=market_pair_id,
        signal_type=signal_type,
        confidence=confidence,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        reason=reason,
        status="PENDING",
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal
