from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional

from app.models import Category, Service, MenuButton
from app.services.maps import get_coordinates_from_address
import asyncio

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

    # Get coordinates from address
    if service_data.get("address"):
        try:
            coordinates = await asyncio.wait_for(
                asyncio.to_thread(get_coordinates_from_address, service_data["address"]),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            coordinates = None
        if coordinates:
            service_data["latitude"], service_data["longitude"] = coordinates

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

async def get_all_services(session: AsyncSession) -> list[Service]:
    """
    Get all services.
    """
    query = select(Service).options(selectinload(Service.category))
    result = await session.execute(query)
    return result.scalars().all()

async def get_service_by_id(session: AsyncSession, service_id: int) -> Optional[Service]:
    """
    Get a service by its ID.
    """
    query = select(Service).where(Service.id == service_id).options(selectinload(Service.category))
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def update_service(session: AsyncSession, service_id: int, service_data: dict) -> Optional[Service]:
    """
    Update a service.
    """
    service = await get_service_by_id(session, service_id)
    if service:
        # Handle category update
        if "category" in service_data:
            category_name = service_data.pop("category")
            query = select(Category).where(Category.name == category_name)
            result = await session.execute(query)
            category = result.scalar_one_or_none()
            if not category:
                category = Category(name=category_name)
                session.add(category)
                await session.flush()
            service.category_id = category.id

        # Get coordinates from address if address is updated
        if "address" in service_data and service_data["address"] != service.address:
             try:
                coordinates = await asyncio.wait_for(
                    asyncio.to_thread(get_coordinates_from_address, service_data["address"]),
                    timeout=5.0
                )
             except asyncio.TimeoutError:
                coordinates = None
             if coordinates:
                service_data["latitude"], service_data["longitude"] = coordinates
             else:
                service_data["latitude"], service_data["longitude"] = None, None


        for key, value in service_data.items():
            setattr(service, key, value)
        
        await session.commit()
        await session.refresh(service, ["category"])
    return service

async def delete_service(session: AsyncSession, service_id: int) -> bool:
    """
    Delete a service.
    """
    service = await get_service_by_id(session, service_id)
    if service:
        await session.delete(service)
        await session.commit()
        return True
    return False

async def get_all_menu_buttons(session: AsyncSession) -> list[MenuButton]:
    """
    Get all menu buttons.
    """
    query = select(MenuButton).options(selectinload(MenuButton.children))
    result = await session.execute(query)
    return result.scalars().all()

async def create_menu_button(session: AsyncSession, button_data: dict) -> MenuButton:
    """
    Create a new menu button.
    """
    new_button = MenuButton(**button_data)
    session.add(new_button)
    await session.commit()
    await session.refresh(new_button)
    return new_button

async def get_menu_button_by_id(session: AsyncSession, button_id: int) -> Optional[MenuButton]:
    """
    Get a menu button by its ID.
    """
    query = select(MenuButton).where(MenuButton.id == button_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def update_menu_button(session: AsyncSession, button_id: int, button_data: dict) -> Optional[MenuButton]:
    """
    Update a menu button.
    """
    button = await get_menu_button_by_id(session, button_id)
    if button:
        for key, value in button_data.items():
            setattr(button, key, value)
        await session.commit()
        await session.refresh(button)
    return button

async def delete_menu_button(session: AsyncSession, button_id: int) -> bool:
    """
    Delete a menu button.
    """
    button = await get_menu_button_by_id(session, button_id)
    if button:
        await session.delete(button)
        await session.commit()
        return True
    return False

async def get_all_categories(session: AsyncSession) -> list[Category]:
    """
    Get all categories.
    """
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()

async def create_category(session: AsyncSession, category_data: dict) -> Category:
    """
    Create a new category.
    """
    new_category = Category(**category_data)
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category

async def get_category_by_id(session: AsyncSession, category_id: int) -> Optional[Category]:
    """
    Get a category by its ID.
    """
    query = select(Category).where(Category.id == category_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def update_category(session: AsyncSession, category_id: int, category_data: dict) -> Optional[Category]:
    """
    Update a category.
    """
    category = await get_category_by_id(session, category_id)
    if category:
        for key, value in category_data.items():
            setattr(category, key, value)
        await session.commit()
        await session.refresh(category)
    return category

async def delete_category(session: AsyncSession, category_id: int) -> bool:
    """
    Delete a category.
    """
    category = await get_category_by_id(session, category_id)
    if category:
        await session.delete(category)
        await session.commit()
        return True
    return False