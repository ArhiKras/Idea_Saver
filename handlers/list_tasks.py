"""
Обработчики команд /list и /list_csv для просмотра задач
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from datetime import datetime
from database import get_all_tasks, get_task_by_id
from keyboards import get_category_keyboard, get_task_actions_keyboard
from utils import export_tasks_to_csv
from .auth import ensure_user_registered
import os

# Создаем роутер
router = Router()


def format_task(task: tuple, show_number: bool = True) -> str:
    """
    Форматирует задачу для вывода
    
    Args:
        task: Кортеж с данными задачи
        show_number: Показывать ли номер в списке
    
    Returns:
        Отформатированная строка с информацией о задаче
    """
    # task = (id, text, status, category, deadline, creator, assignee, created_at)
    task_id, text, status, category, deadline, creator, assignee, created_at = task
    
    # Эмодзи для статусов
    status_emoji = {
        "новое": "🆕",
        "в работе": "⚙️",
        "выполнено": "✅"
    }
    
    # Эмодзи для категорий
    category_emoji = {
        "frontend": "🎨",
        "backend": "⚙️",
        "database": "💾"
    }
    
    # Проверяем дедлайн
    deadline_text = ""
    if deadline:
        try:
            deadline_date = datetime.strptime(deadline, "%d.%m.%Y")
            today = datetime.now()
            
            if deadline_date.date() < today.date():
                deadline_text = f"📅 Дедлайн: ⚠️ {deadline} (просрочен!)"
            else:
                deadline_text = f"📅 Дедлайн: {deadline}"
        except:
            deadline_text = f"📅 Дедлайн: {deadline}"
    else:
        deadline_text = "📅 Дедлайн: Не указан"
    
    # Формируем строку
    result = ""
    if show_number:
        result += f"#{task_id} "
    
    result += f"{text}\n"
    result += f"{status_emoji.get(status, '•')} Статус: {status.capitalize()}\n"
    result += f"{category_emoji.get(category, '📁')} Категория: {category.capitalize()}\n"
    result += f"{deadline_text}\n"
    result += f"👤 Создатель: {creator}\n"
    result += f"👥 Ответственный: {assignee if assignee else 'Не назначен'}\n"
    result += f"🕐 Создано: {created_at}"
    
    return result


@router.message(Command("list"))
async def cmd_list(message: Message):
    """
    Обработчик команды /list
    Выводит список всех задач с возможностью фильтрации
    """
    await ensure_user_registered(message)
    
    # Показываем кнопки фильтрации
    await message.answer(
        "📋 Выберите категорию для фильтрации или посмотрите все задачи:",
        reply_markup=get_category_keyboard(for_filter=True)
    )


@router.message(F.text == "📋 Список задач")
async def button_list(message: Message):
    """
    Обработчик нажатия кнопки "Список задач"
    """
    await cmd_list(message)


@router.callback_query(F.data.startswith("filter:"))
async def filter_tasks(callback: CallbackQuery):
    """
    Обработчик фильтрации задач по категориям
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    # Извлекаем категорию из callback_data
    filter_value = callback.data.split(":")[1]
    
    # Получаем задачи
    if filter_value == "all":
        tasks = await get_all_tasks()
        category_text = "Все категории"
    else:
        tasks = await get_all_tasks(category=filter_value)
        category_text = filter_value.capitalize()
    
    if not tasks:
        await callback.message.edit_text(
            f"📭 Список задач пуст\n"
            f"📁 Фильтр: {category_text}"
        )
        await callback.answer()
        return
    
    # Если задач много, показываем список с кнопками выбора
    if len(tasks) > 10:
        # Создаем кнопки для выбора задачи
        buttons = []
        for task in tasks[:20]:  # Ограничиваем 20 задачами
            task_id, text, status, category, deadline, creator, assignee, created_at = task
            
            # Эмодзи для статусов
            status_emoji = {
                "новое": "🆕",
                "в работе": "⚙️",
                "выполнено": "✅"
            }
            
            button_text = f"{status_emoji.get(status, '•')} #{task_id}: {text[:30]}..."
            buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"task:{task_id}"
                )
            ])
        
        # Добавляем кнопку возврата
        buttons.append([
            InlineKeyboardButton(
                text="◀️ Назад к фильтрам",
                callback_data="back_to_filters"
            )
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback.message.edit_text(
            f"📋 Список задач ({len(tasks)})\n"
            f"📁 Фильтр: {category_text}\n\n"
            f"Выберите задачу для управления:",
            reply_markup=keyboard
        )
    else:
        # Если задач мало, показываем детально с кнопками под каждой
        await show_tasks_with_buttons(callback.message, tasks, category_text, edit=True)
    
    await callback.answer()


async def show_tasks_with_buttons(message, tasks, category_text, edit=False):
    """
    Показывает список задач с inline-кнопками для каждой задачи
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    for i, task in enumerate(tasks):
        task_id = task[0]
        task_text = format_task(task, show_number=True)
        
        # Создаем кнопки для этой задачи
        buttons = [
            [
                InlineKeyboardButton(
                    text="📊 Статус",
                    callback_data=f"change_status:{task_id}"
                ),
                InlineKeyboardButton(
                    text="📁 Категория",
                    callback_data=f"change_category:{task_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete:{task_id}"
                )
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        if i == 0 and edit:
            await message.edit_text(
                f"📋 Задача {i+1} из {len(tasks)}\n"
                f"📁 Фильтр: {category_text}\n\n"
                f"{task_text}",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                f"📋 Задача {i+1} из {len(tasks)}\n"
                f"📁 Фильтр: {category_text}\n\n"
                f"{task_text}",
                reply_markup=keyboard
            )


@router.callback_query(F.data.startswith("task:"))
async def show_task_details(callback: CallbackQuery):
    """
    Показывает детали задачи с кнопками действий
    """
    # Извлекаем ID задачи
    task_id = int(callback.data.split(":")[1])
    
    # Получаем задачу из БД
    task = await get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    # Формируем текст с деталями задачи
    text = f"📋 Задача #{task_id}\n\n"
    text += format_task(task, show_number=False)
    
    # Показываем задачу с кнопками действий
    await callback.message.edit_text(
        text,
        reply_markup=get_task_actions_keyboard(task_id)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_list")
async def back_to_list(callback: CallbackQuery):
    """
    Возврат к списку задач
    """
    await callback.message.delete()
    await callback.message.answer(
        "📋 Выберите категорию для фильтрации или посмотрите все задачи:",
        reply_markup=get_category_keyboard(for_filter=True)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_filters")
async def back_to_filters(callback: CallbackQuery):
    """
    Возврат к фильтрам
    """
    await callback.message.edit_text(
        "📋 Выберите категорию для фильтрации или посмотрите все задачи:",
        reply_markup=get_category_keyboard(for_filter=True)
    )
    await callback.answer()


@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message):
    """
    Обработчик команды /list_csv
    Создает CSV-файл со всеми задачами и отправляет его пользователю
    """
    await ensure_user_registered(message)
    
    # Получаем все задачи
    tasks = await get_all_tasks()
    
    if not tasks:
        await message.answer("📭 Список задач пуст")
        return
    
    # Имя файла
    filename = "tasks.csv"
    
    # Экспортируем задачи в CSV
    await export_tasks_to_csv(tasks, filename)
    
    # Отправляем файл пользователю
    file = FSInputFile(filename)
    await message.answer_document(
        file,
        caption=f"📄 Список всех задач в формате CSV\n"
                f"Всего задач: {len(tasks)}"
    )
    
    # Удаляем временный файл
    os.remove(filename)


@router.message(F.text == "📄 Скачать CSV")
async def button_csv(message: Message):
    """
    Обработчик нажатия кнопки "Скачать CSV"
    """
    await cmd_list_csv(message)

