import asyncio

from app.core.db import async_session_maker
from app.models import Category

async def seed_categories():
    categories = [
        {"name": "Послуги краси", "icon": "💅"},
        {"name": "Автомобільний сервіс", "icon": "🚗"},
        {"name": "Ремонт та обслуговування", "icon": "🏠"},
        {"name": "Розклад транспорту", "icon": "🚌"},
    ]

    async with async_session_maker() as session:
        for cat_data in categories:
            category = Category(**cat_data)
            session.add(category)
        await session.commit()

async def main():
    await seed_categories()

if __name__ == "__main__":
    asyncio.run(main())