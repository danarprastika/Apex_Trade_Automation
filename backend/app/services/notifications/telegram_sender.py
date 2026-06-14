import logging

from app.core.config.settings import settings

logger = logging.getLogger(__name__)


def send_telegram_alert(chat_id: str, message: str) -> None:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("Telegram bot token not configured; skipping alert")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        import httpx

        response = httpx.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as exc:  # pragma: no cover - integration safeguard
        logger.error("Failed to send telegram alert: %s", exc)
