import logging

import httpx

from app.core.config.settings import settings
from app.core.retry import retry_sync

logger = logging.getLogger(__name__)


@retry_sync
def _post_telegram_message(url: str, payload: dict) -> None:
    response = httpx.post(url, json=payload, timeout=10)
    response.raise_for_status()


def send_telegram_alert(chat_id: str, message: str) -> None:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("Telegram bot token not configured; skipping alert")
        return

    url = f"{settings.TELEGRAM_API_BASE_URL.rstrip('/')}/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        _post_telegram_message(url, payload)
    except Exception as exc:  # pragma: no cover - integration safeguard
        logger.error("Failed to send telegram alert after retries: %s", exc)
