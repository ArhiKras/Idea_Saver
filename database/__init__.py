"""
Модуль для работы с базой данных
"""

from .db import init_db, add_task, get_all_tasks

__all__ = ['init_db', 'add_task', 'get_all_tasks']

