from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crud import get_all_menu_buttons

async def main_menu_keyboard(session: AsyncSession) -> ReplyKeyboardMarkup:
    """
    Creates the main menu keyboard from the database.
    """
    buttons_data = await get_all_menu_buttons(session)
    buttons = [[KeyboardButton(text=button.text)] for button in buttons_data if not button.parent_id]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

async def dynamic_keyboard(session: AsyncSession, parent_button_text: str) -> ReplyKeyboardMarkup:
    """
    Creates a dynamic keyboard based on the parent button.
    """
    buttons_data = await get_all_menu_buttons(session)
    parent_button = next((b for b in buttons_data if b.text == parent_button_text), None)
    
    if parent_button:
        buttons = [[KeyboardButton(text=child.text)] for child in parent_button.children]
        buttons.append([KeyboardButton(text="⬅️ Назад")])
    else:
        buttons = [[KeyboardButton(text="⬅️ Назад")]]
        
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard