"""
Inline-клавиатуры для управления статусами задач
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_status_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора статуса задачи
    
    Args:
        task_id: ID задачи
    
    Returns:
        Inline-клавиатура со статусами
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🆕 Новое",
                callback_data=f"status:{task_id}:новое"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚙️ В работе",
                callback_data=f"status:{task_id}:в работе"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Выполнено",
                callback_data=f"status:{task_id}:выполнено"
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"task:{task_id}"
            )
        ]
    ])
    return keyboard


def get_task_actions_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру с действиями для задачи
    
    Args:
        task_id: ID задачи
    
    Returns:
        Inline-клавиатура с кнопками действий
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Изменить статус",
                callback_data=f"change_status:{task_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📁 Изменить категорию",
                callback_data=f"change_category:{task_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑 Удалить задачу",
                callback_data=f"delete:{task_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ К списку",
                callback_data="back_to_list"
            )
        ]
    ])
    return keyboard

