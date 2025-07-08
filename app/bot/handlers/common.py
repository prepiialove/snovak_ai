from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

from app.bot.keyboards.main_menu import main_menu_keyboard

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    This handler receives messages with `/start` command
    """
    welcome_text = (
        f"Вітаю, {message.from_user.full_name}!\n\n"
        "Я ваш персональний помічник по місту Сновськ. "
        "Чим можу допомогти?"
    )
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())