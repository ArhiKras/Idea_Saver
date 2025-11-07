"""
Модуль с обработчиками команд и сообщений бота
"""

from .auth import router as auth_router
from .add_task import router as add_task_router
from .list_tasks import router as list_tasks_router
from .status import router as status_router
from .my_tasks import router as my_tasks_router

# Список всех роутеров для регистрации в main.py
routers = [
    auth_router,
    add_task_router,
    list_tasks_router,
    status_router,
    my_tasks_router
]

__all__ = ['routers']
