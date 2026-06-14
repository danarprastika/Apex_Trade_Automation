import logging
from datetime import UTC, datetime
from typing import Literal
from urllib.parse import urljoin

import httpx
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.database.models.risk import PaperTrade, TradeSide, TradeStatus
from app.database.models.trading import Signal
from app.database.repositories.audit_repository import create_audit_log
from app.services.risk.risk_engine import risk_manager

logger = logging.getLogger(__name__)

SideLiteral = Literal["BUY", "SELL"]


def _send_telegram_alert(chat_id: str, text: str) -> None:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("Telegram bot token not configured; skipping alert")
        return

    url = urljoin(f"https://api.telegram.org/bot{token}/", "sendMessage")
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    try:
        response = httpx.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Failed to send telegram alert: %s", exc)


def _build_trade_notification(trade: PaperTrade, live: bool = False) -> str:
    prefix = "🚨 LIVE TRADE EXECUTED 🚨\n\n" if live else "<b>TRADE OPENED</b>\n\n"
    return prefix + f"Asset: {trade.symbol or 'N/A'}\nSide: {trade.side}\nEntry: {trade.entry_price}\nStrategy: paper-mode"


def execute_paper_trade(db: Session, signal: Signal, user_id, current_price: float, side: SideLiteral = "BUY", telegram_chat_id: str | None = None) -> PaperTrade:
    if not risk_manager.evaluate_signal(db, user_id=user_id, signal=signal):
        raise RuntimeError("Risk blocked execution")

    trade = PaperTrade(
        signal_id=signal.id,
        user_id=user_id,
        symbol=None,
        side=TradeSide(side),
        entry_price=current_price,
        status=TradeStatus.OPEN.value,
        opened_at=datetime.now(UTC),
    )
    db.add(trade)

    signal.status = "EXECUTED"
    db.add(signal)

    create_audit_log(
        db,
        user_id=user_id,
        action="OPEN_POSITION",
        entity_type="paper_trade",
        entity_id="%s" % trade.id,
        new_value={
            "symbol": trade.symbol,
            "side": trade.side.value if isinstance(trade.side, TradeSide) else trade.side,
            "entry_price": "%s" % trade.entry_price,
            "signal_id": "%s" % trade.signal_id,
        },
    )

    db.commit()
    db.refresh(trade)

    if telegram_chat_id:
        _send_telegram_alert(telegram_chat_id, _build_trade_notification(trade, live=False))

    return trade


def execute_real_trade(db: Session, signal: Signal, user_id, current_price: float, side: SideLiteral = "BUY", telegram_chat_id: str | None = None) -> PaperTrade:
    if not risk_manager.evaluate_signal(db, user_id=user_id, signal=signal):
        raise RuntimeError("Risk blocked execution")

    trade = PaperTrade(
        signal_id=signal.id,
        user_id=user_id,
        symbol=None,
        side=TradeSide(side),
        entry_price=current_price,
        status=TradeStatus.OPEN.value,
        opened_at=datetime.now(UTC),
    )
    db.add(trade)

    signal.status = "EXECUTED"
    db.add(signal)

    create_audit_log(
        db,
        user_id=user_id,
        action="OPEN_POSITION",
        entity_type="paper_trade",
        entity_id="%s" % trade.id,
        new_value={
            "symbol": trade.symbol,
            "side": trade.side.value if isinstance(trade.side, TradeSide) else trade.side,
            "entry_price": "%s" % trade.entry_price,
            "signal_id": "%s" % trade.signal_id,
        },
    )

    db.commit()
    db.refresh(trade)

    if telegram_chat_id:
        _send_telegram_alert(telegram_chat_id, _build_trade_notification(trade, live=True))

    return trade


def execute_trade(db: Session, signal: Signal, user_id, current_price: float, side: SideLiteral = "BUY", telegram_chat_id: str | None = None) -> PaperTrade:
    if settings.IS_LIVE_TRADING:
        return execute_real_trade(db, signal, user_id, current_price, side=side, telegram_chat_id=telegram_chat_id)
    return execute_paper_trade(db, signal, user_id, current_price, side=side, telegram_chat_id=telegram_chat_id)
