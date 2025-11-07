"""
Обработчик команды /add для добавления задач
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_task

# Создаем роутер
router = Router()


# Определяем состояния для FSM (Finite State Machine)
class AddTaskStates(StatesGroup):
    waiting_for_task = State()  # Ожидание ввода текста задачи


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """
    Обработчик команды /add
    Проверяет, есть ли текст задачи в команде или запрашивает его
    """
    # Получаем текст после команды /add
    task_text = message.text.replace("/add", "").strip()
    
    if task_text:
        # Если текст задачи указан сразу, сохраняем его
        await save_task(message, task_text)
    else:
        # Если текста нет, просим пользователя ввести его
        await message.answer(
            "📝 Введите текст задачи:"
        )
        # Переводим пользователя в состояние ожидания задачи
        await state.set_state(AddTaskStates.waiting_for_task)


@router.message(F.text == "➕ Добавить задачу")
async def button_add(message: Message, state: FSMContext):
    """
    Обработчик нажатия кнопки "Добавить задачу"
    """
    await message.answer("📝 Введите текст задачи:")
    await state.set_state(AddTaskStates.waiting_for_task)


@router.message(AddTaskStates.waiting_for_task)
async def process_task_text(message: Message, state: FSMContext):
    """
    Обработчик получения текста задачи
    Сохраняет задачу в базу данных
    """
    task_text = message.text.strip()
    
    if task_text:
        await save_task(message, task_text)
        # Сбрасываем состояние
        await state.clear()
    else:
        await message.answer(
            "❌ Задача не может быть пустой. Попробуйте еще раз:"
        )


async def save_task(message: Message, task_text: str):
    """
    Сохраняет задачу в базу данных
    
    Args:
        message: Сообщение от пользователя
        task_text: Текст задачи
    """
    # Получаем имя пользователя
    user_name = message.from_user.full_name
    
    # Добавляем задачу в базу данных
    task_id = await add_task(task_text, user_name)
    
    # Подтверждаем добавление
    await message.answer(
        f"✅ Задача #{task_id} добавлена!\n\n"
        f"📝 {task_text}\n"
        f"👤 Автор: {user_name}"
    )

