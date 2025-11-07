"""
Inline-клавиатуры для управления категориями задач
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_category_keyboard(task_id: int = None, for_filter: bool = False) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора категории
    
    Args:
        task_id: ID задачи (если меняем категорию существующей задачи)
        for_filter: Если True, то клавиатура для фильтра списка
    
    Returns:
        Inline-клавиатура с категориями
    """
    if for_filter:
        # Клавиатура для фильтрации списка
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Frontend",
                    callback_data="filter:frontend"
                ),
                InlineKeyboardButton(
                    text="⚙️ Backend",
                    callback_data="filter:backend"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 Database",
                    callback_data="filter:database"
                ),
                InlineKeyboardButton(
                    text="🔄 Все",
                    callback_data="filter:all"
                )
            ]
        ])
    elif task_id:
        # Клавиатура для изменения категории задачи
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Frontend",
                    callback_data=f"category:{task_id}:frontend"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Backend",
                    callback_data=f"category:{task_id}:backend"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 Database",
                    callback_data=f"category:{task_id}:database"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data=f"task:{task_id}"
                )
            ]
        ])
    else:
        # Клавиатура для выбора категории при создании задачи
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Frontend",
                    callback_data="new_task_category:frontend"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Backend",
                    callback_data="new_task_category:backend"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 Database",
                    callback_data="new_task_category:database"
                )
            ]
        ])
    
    return keyboard


def get_users_keyboard(users: list, prefix: str = "assignee") -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру со списком пользователей для выбора ответственного
    
    Args:
        users: Список пользователей из БД
        prefix: Префикс для callback_data
    
    Returns:
        Inline-клавиатура с пользователями
    """
    buttons = []
    
    for user in users:
        # user = (id, telegram_id, username, full_name)
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {user[3]}",  # full_name
                callback_data=f"{prefix}:{user[0]}"  # user_id
            )
        ])
    
    # Добавляем кнопку "Без ответственного"
    buttons.append([
        InlineKeyboardButton(
            text="❌ Без ответственного",
            callback_data=f"{prefix}:none"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

