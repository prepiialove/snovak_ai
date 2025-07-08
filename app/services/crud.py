from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Service

async def get_services_by_category_name(session: AsyncSession, category_name: str) -> list[Service]:
    """
    Get all services for a given category name.
    """
    query = (
        select(Service)
        .join(Category)
        .where(Category.name == category_name)
        .options(selectinload(Service.category))
    )
    result = await session.execute(query)
    return result.scalars().all()

async def create_service(session: AsyncSession, service_data: dict) -> Service:
    """
    Create a new service.
    """
    # Find the category by name
    category_name = service_data.pop("category")
    query = select(Category).where(Category.name == category_name)
    result = await session.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        # Or create it if it doesn't exist
        category = Category(name=category_name)
        session.add(category)
        await session.flush()

    new_service = Service(**service_data, category_id=category.id)
    session.add(new_service)
    await session.commit()
    await session.refresh(new_service, ["category"])  # Eagerly load the category
    return new_service

async def search_services(session: AsyncSession, query: str) -> list[Service]:
    """
    Search for services by a query string in name and description.
    """
    search_query = f"%{query}%"
    stmt = (
        select(Service)
        .where(
            (Service.name.ilike(search_query)) |
            (Service.description.ilike(search_query))
        )
        .options(selectinload(Service.category))
    )
    result = await session.execute(stmt)
    return result.scalars().all()