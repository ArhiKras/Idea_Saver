"""
Обработчик команды /start
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import get_main_keyboard

# Создаем роутер для обработки сообщений
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    Приветствует пользователя и показывает основные возможности бота
    """
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я бот для командной работы с задачами.\n"
        "Вот что я умею:\n\n"
        "➕ /add <текст> - добавить новую задачу\n"
        "📋 /list - показать все задачи\n"
        "📄 /list_csv - скачать задачи в CSV формате\n\n"
        "Используйте кнопки ниже для удобства! 👇"
    )
    
    # Отправляем приветствие с клавиатурой
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

