"""
Модуль для создания клавиатур бота
"""

from .main_menu import get_main_keyboard
from .status_kb import get_status_keyboard, get_task_actions_keyboard
from .category_kb import get_category_keyboard, get_users_keyboard

__all__ = [
    'get_main_keyboard',
    'get_status_keyboard',
    'get_task_actions_keyboard',
    'get_category_keyboard',
    'get_users_keyboard'
]
