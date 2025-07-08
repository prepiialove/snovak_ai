import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.core.db import async_session_maker
from app.bot.handlers import common, category
from app.bot.middleware.db import DbSessionMiddleware

async def main() -> None:
    # Initialize Bot and Dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register middleware
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session_maker))

    # Register handlers
    dp.include_router(common.router)
    dp.include_router(category.router)

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())