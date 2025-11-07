"""
Обработчик авторизации пользователей
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import get_main_keyboard
from database import add_user, get_user_by_telegram_id

# Создаем роутер для обработки авторизации
router = Router()


async def ensure_user_registered(message: Message) -> int:
    """
    Проверяет регистрацию пользователя и регистрирует при необходимости
    
    Args:
        message: Сообщение от пользователя
    
    Returns:
        ID пользователя в БД
    """
    # Получаем данные пользователя из Telegram
    telegram_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Проверяем, есть ли пользователь в базе
    user = await get_user_by_telegram_id(telegram_id)
    
    if user:
        # Пользователь уже зарегистрирован
        return user[0]  # Возвращаем ID пользователя
    else:
        # Регистрируем нового пользователя
        user_id = await add_user(telegram_id, username, full_name)
        print(f"Новый пользователь зарегистрирован: {full_name} (ID: {user_id})")
        return user_id


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    Регистрирует пользователя и приветствует его
    """
    # Регистрируем/получаем пользователя
    user_id = await ensure_user_registered(message)
    
    # Проверяем, новый ли это пользователь
    user = await get_user_by_telegram_id(message.from_user.id)
    
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я бот для командной работы с задачами.\n"
        "Вот что я умею:\n\n"
        "➕ /add - добавить новую задачу\n"
        "📋 /list - показать все задачи\n"
        "👤 /my_tasks - мои задачи (где я ответственный)\n"
        "📄 /list_csv - скачать задачи в CSV формате\n\n"
        "🆕 Новые возможности:\n"
        "• Статусы задач (новое, в работе, выполнено)\n"
        "• Категории (frontend, backend, database)\n"
        "• Дедлайны\n"
        "• Назначение ответственных\n\n"
        "Используйте кнопки ниже для удобства! 👇"
    )
    
    # Отправляем приветствие с клавиатурой
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

