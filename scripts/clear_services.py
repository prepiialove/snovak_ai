import asyncio

from sqlalchemy import delete
from app.core.db import async_session_maker
from app.models import Service

async def clear_services():
    async with async_session_maker() as session:
        await session.execute(delete(Service))
        await session.commit()

async def main():
    await clear_services()

if __name__ == "__main__":
    asyncio.run(main())