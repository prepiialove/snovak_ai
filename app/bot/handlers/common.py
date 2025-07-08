from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

from app.bot.keyboards.main_menu import main_menu_keyboard, dynamic_keyboard
from app.services.ai import get_service_data_from_text
from app.services.crud import create_service
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

class AdminContact(StatesGroup):
    waiting_for_message = State()
    waiting_for_service_details = State()

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    """
    This handler receives messages with `/start` command
    """
    welcome_text = (
        f"Вітаю, {message.from_user.full_name}!\n\n"
        "Я ваш персональний помічник по місту Сновськ. "
        "Чим можу допомогти?"
    )
    await message.answer(welcome_text, reply_markup=await main_menu_keyboard(session))

@router.message(F.text)
async def handle_dynamic_buttons(message: Message, session: AsyncSession):
    """
    Handles all dynamic buttons.
    """
    if message.text == "⬅️ Назад":
        await message.answer("Головне меню", reply_markup=await main_menu_keyboard(session))
        return

    keyboard = await dynamic_keyboard(session, message.text)
    
    # If the keyboard has more than just a "Back" button, it's a submenu
    if len(keyboard.keyboard) > 1:
        await message.answer(f"Розділ: {message.text}", reply_markup=keyboard)
    else:
        # Otherwise, it's a leaf node, so we can treat it as a category
        # This is a simplification. For a real app, you'd have a more robust way
        # to distinguish between submenus and action buttons.
        await message.answer(f"Тут будуть послуги для категорії '{message.text}'")

@router.message(F.text.in_({"❓ Питання", "💡 Пропозиція", "😡 Скарга", "🤝 Співпраця"}))
async def handle_admin_contact(message: Message, state: FSMContext):
    await state.update_data(contact_type=message.text)
    await message.answer("Будь ласка, напишіть ваше повідомлення і я передам його адміністратору.")
    await state.set_state(AdminContact.waiting_for_message)

@router.message(AdminContact.waiting_for_message)
async def process_admin_message(message: Message, state: FSMContext):
    # Here you would typically forward the message to the admin.
    # For now, we'll just confirm receipt.
    data = await state.get_data()
    contact_type = data.get('contact_type')
    
    # Simulate forwarding to admin
    admin_chat_id = 123456789 # Replace with your admin's chat ID
    await message.forward(chat_id=admin_chat_id)
    
    await message.answer("Дякую, ваше повідомлення було відправлено адміністратору.")
    await state.clear()

@router.message(F.text == "➕ Додати свою послугу")
async def add_own_service(message: Message, state: FSMContext):
    await message.answer("Будь ласка, надішліть детальну інформацію про вашу послугу в одному повідомленні. Наприклад:\n\nНазва: Шиномонтаж 'У Петровича'\nКатегорія: Автомобільний сервіс\nАдреса: вул. Центральна, 10\nТелефон: 0991234567\nГрафік роботи: Пн-Сб 9:00-18:00")
    await state.set_state(AdminContact.waiting_for_service_details)

@router.message(AdminContact.waiting_for_service_details)
async def process_service_details(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Обробляю інформацію...")
    
    service_data = await asyncio.to_thread(get_service_data_from_text, message.text)
    
    if not service_data:
        await message.answer("Вибачте, не вдалося обробити інформацію. Будь ласка, спробуйте ще раз, дотримуючись формату.")
        return

    await create_service(session, service_data.model_dump())
    
    await message.answer("Дякую! Ваша послуга була додана і після перевірки з'явиться в боті.")
    await state.clear()