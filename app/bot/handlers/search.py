import asyncio
import io
from aiogram import Router, F, Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.crud import search_services
from app.services.ai import get_search_query_from_text, translate_to_ukrainian, recognize_speech_from_bytes
from app.bot.handlers.category import show_service_details

router = Router()

# We need to exclude category names from the search handler
# to avoid conflicts with the category handler.
CATEGORY_NAMES = [
    "💅 Послуги краси",
    "🚗 Автомобільний сервіс",
    "🏠 Ремонт та обслуговування",
    "🚌 Розклад транспорту"
]

@router.message(F.voice)
async def handle_voice_message(message: Message, session: AsyncSession, bot: Bot):
    """
    This handler will be called for any voice message.
    It downloads the voice message, converts it to text, and then uses the search logic.
    """
    await message.answer("🎤 Розпізнаю ваше голосове повідомлення...")

    voice_file = await bot.get_file(message.voice.file_id)
    voice_ogg = io.BytesIO()
    await bot.download_file(voice_file.file_path, voice_ogg)
    
    # Recognize speech in a separate thread
    recognized_text = await asyncio.to_thread(recognize_speech_from_bytes, voice_ogg.getvalue())

    if not recognized_text:
        await message.answer("Вибачте, не вдалося розпізнати ваше повідомлення. Спробуйте ще раз.")
        return
    
    await message.answer(f"Ви сказали: \"{recognized_text}\". Шукаю...")
    
    await _process_search_query(message, session, bot, recognized_text)


@router.message(F.text, ~F.text.in_(CATEGORY_NAMES))
async def handle_search_query(message: Message, session: AsyncSession, bot: Bot):
    """
    This handler will be called for any text message that is not a category button.
    It uses AI to get search keywords and then searches the database.
    """
    await message.answer("🔎 Хвилинку, шукаю за вашим запитом...")
    await _process_search_query(message, session, bot, message.text)


async def _process_search_query(message: Message, session: AsyncSession, bot: Bot, text: str):
    # Translate the message to Ukrainian in a separate thread to avoid blocking
    ukrainian_text = await asyncio.to_thread(translate_to_ukrainian, text)

    # Get search query from the translated text in a separate thread
    search_query = await asyncio.to_thread(get_search_query_from_text, ukrainian_text)

    if not search_query:
        await message.answer("Вибачте, не вдалося обробити ваш запит. Спробуйте перефразувати.")
        return

    services = await search_services(session, search_query)

    if not services:
        await message.answer(f"🤷 На жаль, за запитом '{search_query}' нічого не знайдено. Спробуйте інший запит.")
        return

    await message.answer(f"<b>Знайдено за запитом '{search_query}':</b>")

    for service in services:
        # We can reuse the function from the category handler to display the service details
        # by creating a "fake" message with the command.
        fake_message = message
        fake_message.text = f"/service_{service.id}"
        await show_service_details(fake_message, session, bot)