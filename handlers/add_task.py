"""
Обработчик команды /add для добавления задач с расширенными параметрами
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from database import add_task, get_all_users
from keyboards import get_category_keyboard, get_users_keyboard
from .auth import ensure_user_registered

# Создаем роутер
router = Router()


# Определяем состояния для FSM (Finite State Machine)
class AddTaskStates(StatesGroup):
    waiting_for_text = State()  # Ожидание текста задачи
    waiting_for_category = State()  # Ожидание выбора категории
    waiting_for_deadline = State()  # Ожидание ввода дедлайна
    waiting_for_assignee = State()  # Ожидание выбора ответственного


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """
    Обработчик команды /add
    Начинает процесс добавления задачи
    """
    # Проверяем/регистрируем пользователя
    await ensure_user_registered(message)
    
    await message.answer("📝 Введите текст задачи:")
    await state.set_state(AddTaskStates.waiting_for_text)


@router.message(F.text == "➕ Добавить задачу")
async def button_add(message: Message, state: FSMContext):
    """
    Обработчик нажатия кнопки "Добавить задачу"
    """
    await ensure_user_registered(message)
    await message.answer("📝 Введите текст задачи:")
    await state.set_state(AddTaskStates.waiting_for_text)


@router.message(AddTaskStates.waiting_for_text)
async def process_task_text(message: Message, state: FSMContext):
    """
    Обработчик получения текста задачи
    Переходит к выбору категории
    """
    task_text = message.text.strip()
    
    if not task_text:
        await message.answer("❌ Задача не может быть пустой. Попробуйте еще раз:")
        return
    
    # Сохраняем текст задачи в состоянии
    await state.update_data(task_text=task_text)
    
    # Предлагаем выбрать категорию
    await message.answer(
        "📁 Выберите категорию задачи:",
        reply_markup=get_category_keyboard()
    )
    await state.set_state(AddTaskStates.waiting_for_category)


@router.callback_query(F.data.startswith("new_task_category:"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора категории
    Переходит к вводу дедлайна
    """
    # Извлекаем категорию из callback_data
    category = callback.data.split(":")[1]
    
    # Сохраняем категорию
    await state.update_data(category=category)
    
    # Эмодзи для категорий
    category_emoji = {
        "frontend": "🎨",
        "backend": "⚙️",
        "database": "💾"
    }
    
    await callback.message.edit_text(
        f"✅ Категория: {category_emoji.get(category, '')} {category.capitalize()}"
    )
    
    await callback.message.answer(
        "📅 Введите дедлайн в формате ДД.ММ.ГГГГ\n"
        "Или отправьте '-' если дедлайн не нужен:"
    )
    await state.set_state(AddTaskStates.waiting_for_deadline)
    await callback.answer()


@router.message(AddTaskStates.waiting_for_deadline)
async def process_deadline(message: Message, state: FSMContext):
    """
    Обработчик ввода дедлайна
    Переходит к выбору ответственного
    """
    deadline_text = message.text.strip()
    
    # Проверяем формат дедлайна
    if deadline_text == "-":
        deadline = None
    else:
        try:
            # Проверяем корректность даты
            datetime.strptime(deadline_text, "%d.%m.%Y")
            deadline = deadline_text
        except ValueError:
            await message.answer(
                "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
                "Например: 31.12.2024\n"
                "Или отправьте '-' для пропуска:"
            )
            return
    
    # Сохраняем дедлайн
    await state.update_data(deadline=deadline)
    
    # Получаем список пользователей для выбора ответственного
    users = await get_all_users()
    
    if users:
        await message.answer(
            "👤 Выберите ответственного за задачу:",
            reply_markup=get_users_keyboard(users, prefix="new_task_assignee")
        )
        await state.set_state(AddTaskStates.waiting_for_assignee)
    else:
        # Если пользователей нет, сохраняем задачу без ответственного
        await save_task(message, state, None)


@router.callback_query(F.data.startswith("new_task_assignee:"))
async def process_assignee(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора ответственного
    Сохраняет задачу в БД
    """
    # Извлекаем ID ответственного
    assignee_data = callback.data.split(":")[1]
    assignee_id = None if assignee_data == "none" else int(assignee_data)
    
    await callback.message.delete()
    # Передаем callback вместо message для получения правильного user_id
    await save_task_from_callback(callback, state, assignee_id)
    await callback.answer()


async def save_task(message: Message, state: FSMContext, assignee_id: int = None):
    """
    Сохраняет задачу в базу данных
    
    Args:
        message: Сообщение от пользователя
        state: Состояние FSM
        assignee_id: ID ответственного пользователя
    """
    # Получаем все данные из состояния
    data = await state.get_data()
    task_text = data.get("task_text")
    category = data.get("category")
    deadline = data.get("deadline")
    
    # Получаем ID текущего пользователя
    from database import get_user_by_telegram_id
    user = await get_user_by_telegram_id(message.from_user.id)
    user_id = user[0]
    
    await _save_task_to_db(message, task_text, category, deadline, user_id, assignee_id, state)


async def save_task_from_callback(callback: CallbackQuery, state: FSMContext, assignee_id: int = None):
    """
    Сохраняет задачу в базу данных из callback
    
    Args:
        callback: CallbackQuery от пользователя
        state: Состояние FSM
        assignee_id: ID ответственного пользователя
    """
    # Получаем все данные из состояния
    data = await state.get_data()
    task_text = data.get("task_text")
    category = data.get("category")
    deadline = data.get("deadline")
    
    # Получаем ID текущего пользователя из callback
    from database import get_user_by_telegram_id
    user = await get_user_by_telegram_id(callback.from_user.id)
    user_id = user[0]
    
    # Используем callback.message для отправки ответа
    await _save_task_to_db(callback.message, task_text, category, deadline, user_id, assignee_id, state)


async def _save_task_to_db(message: Message, task_text: str, category: str, deadline: str, user_id: int, assignee_id: int, state: FSMContext):
    """
    Внутренняя функция для сохранения задачи в БД
    
    Args:
        message: Сообщение для отправки ответа
        task_text: Текст задачи
        category: Категория задачи
        deadline: Дедлайн задачи
        user_id: ID создателя задачи
        assignee_id: ID ответственного пользователя
        state: Состояние FSM
    """
    
    # Добавляем задачу в базу данных
    task_id = await add_task(
        text=task_text,
        user_id=user_id,
        status="новое",
        category=category,
        deadline=deadline,
        assignee_id=assignee_id
    )
    
    # Формируем сообщение о созданной задаче
    category_emoji = {
        "frontend": "🎨",
        "backend": "⚙️",
        "database": "💾"
    }
    
    result_text = (
        f"✅ Задача #{task_id} создана!\n\n"
        f"📝 {task_text}\n"
        f"📁 Категория: {category_emoji.get(category, '')} {category.capitalize()}\n"
        f"📅 Дедлайн: {deadline if deadline else 'Не указан'}\n"
        f"🆕 Статус: Новое"
    )
    
    if assignee_id:
        from database import get_all_users
        users = await get_all_users()
        assignee = next((u for u in users if u[0] == assignee_id), None)
        if assignee:
            result_text += f"\n👤 Ответственный: {assignee[3]}"
    else:
        result_text += "\n👤 Ответственный: Не назначен"
    
    await message.answer(result_text)
    
    # Очищаем состояние
    await state.clear()

