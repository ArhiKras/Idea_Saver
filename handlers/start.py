"""
Обработчик команды /start (импорт из auth.py)
"""

from .auth import router

# Экспортируем роутер из auth.py
__all__ = ['router']
