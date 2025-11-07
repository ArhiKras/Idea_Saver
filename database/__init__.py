"""
Модуль для работы с базой данных
"""

from .db import (
    init_db,
    add_user,
    get_user_by_telegram_id,
    get_all_users,
    add_task,
    get_all_tasks,
    get_user_tasks,
    update_task_status,
    update_task_category,
    delete_task,
    get_task_by_id
)

__all__ = [
    'init_db',
    'add_user',
    'get_user_by_telegram_id',
    'get_all_users',
    'add_task',
    'get_all_tasks',
    'get_user_tasks',
    'update_task_status',
    'update_task_category',
    'delete_task',
    'get_task_by_id'
]
