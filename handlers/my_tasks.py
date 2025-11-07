"""
Обработчик команды /my_tasks для просмотра задач пользователя
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database import get_user_tasks, get_user_by_telegram_id
from .auth import ensure_user_registered
from .list_tasks import format_task

# Создаем роутер
router = Router()


@router.message(Command("my_tasks"))
async def cmd_my_tasks(message: Message):
    """
    Обработчик команды /my_tasks
    Выводит задачи, где пользователь является ответственным
    """
    # Регистрируем/получаем пользователя
    await ensure_user_registered(message)
    
    # Получаем ID пользователя из БД
    user = await get_user_by_telegram_id(message.from_user.id)
    user_id = user[0]
    
    # Получаем задачи пользователя
    tasks = await get_user_tasks(user_id)
    
    if not tasks:
        await message.answer(
            "📭 У вас нет задач, где вы назначены ответственным"
        )
        return
    
    # Формируем текст со списком задач
    text = f"👤 Мои задачи ({len(tasks)}):\n"
    text += f"Вы назначены ответственным\n\n"
    
    for task in tasks:
        text += format_task(task) + "\n"
        text += "─" * 30 + "\n\n"
    
    # Отправляем список задач
    # Telegram ограничивает длину сообщения 4096 символами
    if len(text) > 4096:
        # Если текст слишком длинный, разбиваем на части
        for i in range(0, len(text), 4096):
            await message.answer(text[i:i+4096])
    else:
        await message.answer(text)


@router.message(F.text == "👤 Мои задачи")
async def button_my_tasks(message: Message):
    """
    Обработчик нажатия кнопки "Мои задачи"
    """
    await cmd_my_tasks(message)

