import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from telegram_bot.handlers.start import start_router
from telegram_bot.handlers.help import help_router
from telegram_bot.handlers.status import status_router

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")

logging.basicConfig(level=logging.INFO)


def create_bot() -> Bot:
    return Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(start_router)
    dispatcher.include_router(status_router)
    dispatcher.include_router(help_router)
    return dispatcher


bot = create_bot()
dispatcher = create_dispatcher()
