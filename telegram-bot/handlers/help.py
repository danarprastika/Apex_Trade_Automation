from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def help_command(message: Message) -> None:
    help_text = (
        "<b>Menu APEX Bot</b>\n\n"
        "/start - Sambungkan akun ke APEX\n"
        "/status - Cek status sistem backend dan collector\n"
        "/help - Tampilkan pesan bantuan ini\n"
    )
    await message.answer(help_text)
