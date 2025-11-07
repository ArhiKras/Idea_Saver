"""
Модуль для работы с SQLite базой данных
Содержит функции для создания таблиц и работы с задачами
"""

import aiosqlite
from datetime import datetime

# Путь к файлу базы данных
DATABASE_PATH = "tasks.db"


async def init_db():
    """
    Инициализация базы данных
    Создает таблицу tasks, если она еще не существует
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Создаем таблицу tasks с полями:
        # id - уникальный идентификатор (автоинкремент)
        # text - текст задачи
        # user - имя пользователя, добавившего задачу
        # created_at - дата и время создания задачи
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                user TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()
        print("База данных инициализирована")


async def add_task(text: str, user: str) -> int:
    """
    Добавление новой задачи в базу данных
    
    Args:
        text: Текст задачи
        user: Имя пользователя, добавившего задачу
    
    Returns:
        ID добавленной задачи
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Получаем текущее время
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Вставляем новую задачу в таблицу
        cursor = await db.execute(
            "INSERT INTO tasks (text, user, created_at) VALUES (?, ?, ?)",
            (text, user, created_at)
        )
        await db.commit()
        
        # Возвращаем ID добавленной задачи
        return cursor.lastrowid


async def get_all_tasks() -> list:
    """
    Получение всех задач из базы данных
    
    Returns:
        Список кортежей с данными задач (id, text, user, created_at)
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Получаем все задачи, отсортированные по дате создания
        cursor = await db.execute(
            "SELECT id, text, user, created_at FROM tasks ORDER BY created_at DESC"
        )
        tasks = await cursor.fetchall()
        return tasks

