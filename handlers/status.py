"""
Обработчики для изменения статусов и категорий задач
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import (
    update_task_status,
    update_task_category,
    delete_task,
    get_task_by_id
)
from keyboards import get_status_keyboard, get_category_keyboard, get_task_actions_keyboard

# Создаем роутер
router = Router()


@router.callback_query(F.data.startswith("change_status:"))
async def change_status_menu(callback: CallbackQuery):
    """
    Показывает меню выбора статуса
    """
    # Извлекаем ID задачи
    task_id = int(callback.data.split(":")[1])
    
    # Получаем задачу
    task = await get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    # Показываем меню выбора статуса
    await callback.message.edit_text(
        f"📋 Задача #{task_id}\n"
        f"📝 {task[1]}\n\n"
        f"Текущий статус: {task[2]}\n\n"
        f"Выберите новый статус:",
        reply_markup=get_status_keyboard(task_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("status:"))
async def update_status(callback: CallbackQuery):
    """
    Обновляет статус задачи
    """
    # Извлекаем данные: status:task_id:new_status
    parts = callback.data.split(":")
    task_id = int(parts[1])
    new_status = parts[2]
    
    # Обновляем статус в БД
    await update_task_status(task_id, new_status)
    
    # Получаем обновленную задачу
    task = await get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    # Эмодзи для статусов
    status_emoji = {
        "новое": "🆕",
        "в работе": "⚙️",
        "выполнено": "✅"
    }
    
    # Формируем текст с обновленной информацией
    from .list_tasks import format_task
    text = f"📋 Задача #{task_id}\n\n"
    text += format_task(task, show_number=False)
    text += f"\n\n✅ Статус изменен на: {status_emoji.get(new_status, '')} {new_status.capitalize()}"
    
    # Показываем обновленную задачу
    await callback.message.edit_text(
        text,
        reply_markup=get_task_actions_keyboard(task_id)
    )
    await callback.answer(f"✅ Статус изменен на: {new_status}")


@router.callback_query(F.data.startswith("change_category:"))
async def change_category_menu(callback: CallbackQuery):
    """
    Показывает меню выбора категории
    """
    # Извлекаем ID задачи
    task_id = int(callback.data.split(":")[1])
    
    # Получаем задачу
    task = await get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    # Показываем меню выбора категории
    await callback.message.edit_text(
        f"📋 Задача #{task_id}\n"
        f"📝 {task[1]}\n\n"
        f"Текущая категория: {task[3]}\n\n"
        f"Выберите новую категорию:",
        reply_markup=get_category_keyboard(task_id=task_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category:"))
async def update_category(callback: CallbackQuery):
    """
    Обновляет категорию задачи
    """
    # Извлекаем данные: category:task_id:new_category
    parts = callback.data.split(":")
    task_id = int(parts[1])
    new_category = parts[2]
    
    # Обновляем категорию в БД
    await update_task_category(task_id, new_category)
    
    # Получаем обновленную задачу
    task = await get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    # Эмодзи для категорий
    category_emoji = {
        "frontend": "🎨",
        "backend": "⚙️",
        "database": "💾"
    }
    
    # Формируем текст с обновленной информацией
    from .list_tasks import format_task
    text = f"📋 Задача #{task_id}\n\n"
    text += format_task(task, show_number=False)
    text += f"\n\n✅ Категория изменена на: {category_emoji.get(new_category, '')} {new_category.capitalize()}"
    
    # Показываем обновленную задачу
    await callback.message.edit_text(
        text,
        reply_markup=get_task_actions_keyboard(task_id)
    )
    await callback.answer(f"✅ Категория изменена на: {new_category}")


@router.callback_query(F.data.startswith("delete:"))
async def delete_task_handler(callback: CallbackQuery):
    """
    Удаляет задачу
    """
    # Извлекаем ID задачи
    task_id = int(callback.data.split(":")[1])
    
    # Удаляем задачу из БД
    await delete_task(task_id)
    
    await callback.message.edit_text(
        f"🗑 Задача #{task_id} удалена"
    )
    await callback.answer("✅ Задача удалена")

