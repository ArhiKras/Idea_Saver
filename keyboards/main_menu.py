"""
Основное меню бота
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает основную клавиатуру с кнопками команд
    
    Returns:
        Клавиатура с кнопками для основных команд
    """
    # Создаем кнопки
    button_add = KeyboardButton(text="➕ Добавить задачу")
    button_list = KeyboardButton(text="📋 Список задач")
    button_my_tasks = KeyboardButton(text="👤 Мои задачи")
    button_csv = KeyboardButton(text="📄 Скачать CSV")
    
    # Создаем клавиатуру
    # resize_keyboard=True - делает кнопки компактными
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_add],
            [button_list, button_my_tasks],
            [button_csv]
        ],
        resize_keyboard=True
    )
    
    return keyboard

