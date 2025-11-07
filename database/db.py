"""
Модуль для работы с SQLite базой данных
Содержит функции для создания таблиц и работы с задачами и пользователями
"""

import aiosqlite
from datetime import datetime
from typing import Optional, List, Tuple

# Путь к файлу базы данных
DATABASE_PATH = "tasks.db"


async def init_db():
    """
    Инициализация базы данных
    Создает таблицы users и tasks, если они еще не существуют
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Создаем таблицу пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Создаем новую таблицу задач с расширенными полями
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'новое',
                category TEXT DEFAULT 'backend',
                deadline TEXT,
                assignee_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assignee_id) REFERENCES users (id)
            )
        """)
        
        await db.commit()
        print("База данных инициализирована")


async def add_user(telegram_id: int, username: Optional[str], full_name: str) -> int:
    """
    Добавление нового пользователя в базу данных
    
    Args:
        telegram_id: Telegram ID пользователя
        username: Username пользователя (может быть None)
        full_name: Полное имя пользователя
    
    Returns:
        ID добавленного пользователя
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            cursor = await db.execute(
                "INSERT INTO users (telegram_id, username, full_name, created_at) VALUES (?, ?, ?, ?)",
                (telegram_id, username, full_name, created_at)
            )
            await db.commit()
            return cursor.lastrowid
        except aiosqlite.IntegrityError:
            # Пользователь уже существует, получаем его ID
            cursor = await db.execute(
                "SELECT id FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else None


async def get_user_by_telegram_id(telegram_id: int) -> Optional[Tuple]:
    """
    Получение пользователя по Telegram ID
    
    Args:
        telegram_id: Telegram ID пользователя
    
    Returns:
        Кортеж с данными пользователя или None
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id, telegram_id, username, full_name FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return await cursor.fetchone()


async def get_all_users() -> List[Tuple]:
    """
    Получение всех пользователей
    
    Returns:
        Список кортежей с данными пользователей
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id, telegram_id, username, full_name FROM users ORDER BY full_name"
        )
        return await cursor.fetchall()


async def add_task(
    text: str,
    user_id: int,
    status: str = "новое",
    category: str = "backend",
    deadline: Optional[str] = None,
    assignee_id: Optional[int] = None
) -> int:
    """
    Добавление новой задачи в базу данных
    
    Args:
        text: Текст задачи
        user_id: ID пользователя, создавшего задачу
        status: Статус задачи (по умолчанию "новое")
        category: Категория задачи
        deadline: Дедлайн в формате ДД.ММ.ГГГГ
        assignee_id: ID ответственного пользователя
    
    Returns:
        ID добавленной задачи
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = await db.execute(
            """INSERT INTO tasks 
            (text, user_id, status, category, deadline, assignee_id, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (text, user_id, status, category, deadline, assignee_id, created_at)
        )
        await db.commit()
        return cursor.lastrowid


async def get_all_tasks(category: Optional[str] = None) -> List[Tuple]:
    """
    Получение всех задач из базы данных
    
    Args:
        category: Фильтр по категории (если указан)
    
    Returns:
        Список кортежей с данными задач
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        if category:
            cursor = await db.execute(
                """SELECT t.id, t.text, t.status, t.category, t.deadline, 
                          u1.full_name as creator, u2.full_name as assignee, t.created_at
                   FROM tasks t
                   LEFT JOIN users u1 ON t.user_id = u1.id
                   LEFT JOIN users u2 ON t.assignee_id = u2.id
                   WHERE t.category = ?
                   ORDER BY t.created_at DESC""",
                (category,)
            )
        else:
            cursor = await db.execute(
                """SELECT t.id, t.text, t.status, t.category, t.deadline, 
                          u1.full_name as creator, u2.full_name as assignee, t.created_at
                   FROM tasks t
                   LEFT JOIN users u1 ON t.user_id = u1.id
                   LEFT JOIN users u2 ON t.assignee_id = u2.id
                   ORDER BY t.created_at DESC"""
            )
        return await cursor.fetchall()


async def get_user_tasks(user_id: int) -> List[Tuple]:
    """
    Получение задач конкретного пользователя (где он ответственный)
    
    Args:
        user_id: ID пользователя
    
    Returns:
        Список кортежей с данными задач
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """SELECT t.id, t.text, t.status, t.category, t.deadline, 
                      u1.full_name as creator, u2.full_name as assignee, t.created_at
               FROM tasks t
               LEFT JOIN users u1 ON t.user_id = u1.id
               LEFT JOIN users u2 ON t.assignee_id = u2.id
               WHERE t.assignee_id = ?
               ORDER BY t.created_at DESC""",
            (user_id,)
        )
        return await cursor.fetchall()


async def update_task_status(task_id: int, status: str) -> bool:
    """
    Обновление статуса задачи
    
    Args:
        task_id: ID задачи
        status: Новый статус
    
    Returns:
        True если обновление успешно
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )
        await db.commit()
        return True


async def update_task_category(task_id: int, category: str) -> bool:
    """
    Обновление категории задачи
    
    Args:
        task_id: ID задачи
        category: Новая категория
    
    Returns:
        True если обновление успешно
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE tasks SET category = ? WHERE id = ?",
            (category, task_id)
        )
        await db.commit()
        return True


async def delete_task(task_id: int) -> bool:
    """
    Удаление задачи
    
    Args:
        task_id: ID задачи
    
    Returns:
        True если удаление успешно
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()
        return True


async def get_task_by_id(task_id: int) -> Optional[Tuple]:
    """
    Получение задачи по ID
    
    Args:
        task_id: ID задачи
    
    Returns:
        Кортеж с данными задачи или None
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """SELECT t.id, t.text, t.status, t.category, t.deadline, 
                      u1.full_name as creator, u2.full_name as assignee, t.created_at
               FROM tasks t
               LEFT JOIN users u1 ON t.user_id = u1.id
               LEFT JOIN users u2 ON t.assignee_id = u2.id
               WHERE t.id = ?""",
            (task_id,)
        )
        return await cursor.fetchone()
