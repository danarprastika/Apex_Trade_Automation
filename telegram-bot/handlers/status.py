import os

import httpx
from aiogram import Router
from aiogram.types import Message

router = Router()

BACKEND_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")


@router.message()
async def status_command(message: Message) -> None:
    if not BACKEND_BASE_URL:
        await message.answer("API_BASE_URL is not configured.")
        return
    try:
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=5) as client:
            resp = await client.get("/health")
            data = resp.json()
    except Exception as exc:
        await message.answer(f"Gagal menghubungi backend: {exc}")
        return

    status_text = (
        "<b>Status Sistem APEX</b>\n\n"
        f"Backend: {data.get('status', 'unknown')}\n"
    )
    await message.answer(status_text)
