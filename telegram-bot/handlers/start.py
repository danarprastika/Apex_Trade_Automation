from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def start_command(message: Message) -> None:
    welcome_text = (
        "Selamat datang di <b>APEX Financial Intelligence Platform</b>.\n\n"
        "Gunakan perintah berikut untuk memulai:\n"
        "/help - Lihat menu bantuan\n"
        "/status - Cek status sistem backend dan collector\n\n"
        "Untuk menautkan akun Anda, silakan gunakan tombol verifikasi yang akan dikirimkan di tahap berikutnya."
    )
    await message.answer(welcome_text)
