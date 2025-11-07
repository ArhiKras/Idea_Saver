"""
Обработчики команд /list и /list_csv для просмотра задач
"""

import csv
import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from database import get_all_tasks

# Создаем роутер
router = Router()


@router.message(Command("list"))
async def cmd_list(message: Message):
    """
    Обработчик команды /list
    Выводит список всех задач из базы данных
    """
    # Получаем все задачи из базы данных
    tasks = await get_all_tasks()
    
    if not tasks:
        # Если задач нет
        await message.answer("📭 Список задач пуст")
        return
    
    # Формируем текст со списком задач
    text = f"📋 Список задач ({len(tasks)}):\n\n"
    
    for task in tasks:
        task_id, task_text, user, created_at = task
        text += (
            f"#{task_id} {task_text}\n"
            f"👤 {user} | 🕐 {created_at}\n"
            f"{'─' * 30}\n"
        )
    
    # Отправляем список задач
    # Telegram ограничивает длину сообщения 4096 символами
    if len(text) > 4096:
        # Если текст слишком длинный, разбиваем на части
        for i in range(0, len(text), 4096):
            await message.answer(text[i:i+4096])
    else:
        await message.answer(text)


@router.message(F.text == "📋 Список задач")
async def button_list(message: Message):
    """
    Обработчик нажатия кнопки "Список задач"
    """
    await cmd_list(message)


@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message):
    """
    Обработчик команды /list_csv
    Создает CSV-файл со всеми задачами и отправляет его пользователю
    """
    # Получаем все задачи
    tasks = await get_all_tasks()
    
    if not tasks:
        await message.answer("📭 Список задач пуст")
        return
    
    # Имя файла
    filename = "tasks.csv"
    
    # Создаем CSV-файл
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        # Создаем writer для записи в CSV
        writer = csv.writer(csvfile)
        
        # Записываем заголовки
        writer.writerow(['ID', 'Задача', 'Автор', 'Дата создания'])
        
        # Записываем данные задач
        for task in tasks:
            writer.writerow(task)
    
    # Отправляем файл пользователю
    file = FSInputFile(filename)
    await message.answer_document(
        file,
        caption="📄 Список всех задач в формате CSV"
    )
    
    # Удаляем временный файл
    os.remove(filename)


@router.message(F.text == "📄 Скачать CSV")
async def button_csv(message: Message):
    """
    Обработчик нажатия кнопки "Скачать CSV"
    """
    await cmd_list_csv(message)

