"""
Модуль с обработчиками команд и сообщений бота
"""

from .start import router as start_router
from .add import router as add_router
from .list import router as list_router

# Список всех роутеров для регистрации в main.py
routers = [start_router, add_router, list_router]

__all__ = ['routers']

