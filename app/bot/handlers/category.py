from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.crud import get_services_by_category_name

router = Router()

# This is a simple filter to catch category buttons based on the emoji
@router.message(F.text.endswith("Послуги краси") | F.text.endswith("Автомобільний сервіс") | F.text.endswith("Ремонт та обслуговування") | F.text.endswith("Розклад транспорту"))
async def show_category(message: Message, session: AsyncSession):
    """
    This handler will be called when user clicks on a category button
    """
    category_name = message.text.lstrip("💅🚗🏠🚌 ")
    services = await get_services_by_category_name(session, category_name)

    if not services:
        await message.answer(f"На жаль, у категорії '{category_name}' поки що немає жодної послуги.")
        return

    response_text = f"<b>Послуги в категорії '{category_name}':</b>\n\n"
    for service in services:
        response_text += f"<b>{service.name}</b>\n"
        if service.address:
            response_text += f"📍 {service.address}\n"
        if service.phone:
            response_text += f"📞 {service.phone}\n"
        if service.schedule:
            response_text += f"🕒 {service.schedule}\n"
        if service.description:
            response_text += f"📝 {service.description}\n"
        response_text += "\n"

    await message.answer(response_text)