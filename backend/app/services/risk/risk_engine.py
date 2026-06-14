from sqlalchemy.orm import Session

from app.core.exceptions.exceptions import APEXException
from app.database.models.risk import PaperTrade, RiskSettings


class RiskManager:
    def evaluate_signal(self, db: Session, user_id, signal) -> bool:
        settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
        if not settings:
            return True

        if settings.max_open_positions is not None:
            open_count = (
                db.query(PaperTrade)
                .filter(PaperTrade.user_id == user_id, PaperTrade.status == "OPEN")
                .count()
            )
            if open_count >= settings.max_open_positions:
                raise APEXException("Max open positions reached", status_code=400)

        return True


risk_manager = RiskManager()
