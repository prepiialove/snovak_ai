from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Creates the main menu keyboard
    """
    buttons = [
        [KeyboardButton(text="💅 Послуги краси")],
        [KeyboardButton(text="🚗 Автомобільний сервіс")],
        [KeyboardButton(text="🏠 Ремонт та обслуговування")],
        [KeyboardButton(text="🚌 Розклад транспорту")],
        [KeyboardButton(text="🗺️ Показати на мапі")],
        [KeyboardButton(text="✍️ Зв'язок з адміністратором")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard