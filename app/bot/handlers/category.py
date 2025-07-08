from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from app.services.crud import get_services_by_category_name, get_service_by_id
from app.bot.keyboards.callbacks import ServiceCallback, PaginationCallback

router = Router()
SERVICES_PER_PAGE = 5

# This is a simple filter to catch category buttons based on the emoji
@router.message(F.text.endswith("Послуги краси") | F.text.endswith("Автомобільний сервіс") | F.text.endswith("Ремонт та обслуговування") | F.text.endswith("Розклад транспорту"))
async def show_category(message: Message, session: AsyncSession):
    """
    This handler will be called when user clicks on a category button
    """
    category_name = message.text.lstrip("💅🚗🏠🚌 ")
    await send_paginated_services(message, session, category_name, page=1)


@router.callback_query(PaginationCallback.filter(F.action.in_(["prev", "next"])))
async def handle_pagination(query: CallbackQuery, callback_data: PaginationCallback, session: AsyncSession):
    await query.answer()
    page = callback_data.page
    category_name = callback_data.category_name
    await send_paginated_services(query.message, session, category_name, page, is_edit=True)


async def send_paginated_services(message: Message, session: AsyncSession, category_name: str, page: int, is_edit: bool = False):
    services = await get_services_by_category_name(session, category_name)
    
    if not services:
        await message.answer(f"На жаль, у категорії '{category_name}' поки що немає жодної послуги.")
        return

    total_pages = ceil(len(services) / SERVICES_PER_PAGE)
    start_index = (page - 1) * SERVICES_PER_PAGE
    end_index = start_index + SERVICES_PER_PAGE
    paginated_services = services[start_index:end_index]

    response_text = f"<b>Послуги в категорії '{category_name}' (Сторінка {page}/{total_pages}):</b>\n\n"
    
    for service in paginated_services:
        response_text += f"<b>{service.name}</b>\n"
        if service.address:
            response_text += f"📍 {service.address}\n"
        response_text += f" chi tiết: /service_{service.id}\n\n"

    # Pagination keyboard
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=PaginationCallback(action="prev", page=page-1, category_name=category_name).pack()))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=PaginationCallback(action="next", page=page+1, category_name=category_name).pack()))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

    if is_edit:
        await message.edit_text(response_text, reply_markup=keyboard)
    else:
        await message.answer(response_text, reply_markup=keyboard)


@router.message(F.text.startswith("/service_"))
async def show_service_details(message: Message, session: AsyncSession, bot: Bot):
    service_id = int(message.text.split("_")[1])
    service = await get_service_by_id(session, service_id)

    if not service:
        await message.answer("Послугу не знайдено.")
        return

    response_text = f"<b>{service.name}</b>\n\n"
    if service.description:
        response_text += f"📝 {service.description}\n"
    if service.address:
        response_text += f"📍 {service.address}\n"
    if service.phone:
        response_text += f"📞 {service.phone}\n"
    if service.schedule:
        response_text += f"🕒 {service.schedule}\n"
    if service.social_media:
        response_text += f"🌐 {service.social_media}\n"

    buttons = []
    if service.latitude and service.longitude:
        buttons.append(InlineKeyboardButton(text="🗺️ Показати на мапі", callback_data=ServiceCallback(action="show_map", service_id=service.id).pack()))
    if service.phone:
        buttons.append(InlineKeyboardButton(text="📞 Подзвонити", url=f"tel:{service.phone}"))
    if service.social_media:
        buttons.append(InlineKeyboardButton(text="🌐 Перейти на сайт", url=service.social_media))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.answer(response_text, reply_markup=keyboard)


@router.callback_query(ServiceCallback.filter(F.action == "show_map"))
async def handle_show_map(query: CallbackQuery, callback_data: ServiceCallback, session: AsyncSession, bot: Bot):
    await query.answer()
    service = await get_service_by_id(session, callback_data.service_id)
    if service and service.latitude and service.longitude:
        await bot.send_location(query.from_user.id, latitude=service.latitude, longitude=service.longitude)