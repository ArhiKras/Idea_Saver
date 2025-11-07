"""
Главный файл Telegram-бота для командной работы с задачами

Расширенная версия с поддержкой:
- Статусов задач (новое, в работе, выполнено)
- Категорий (frontend, backend, database)
- Дедлайнов
- Назначения ответственных
- Авторизации пользователей

Запуск бота:
1. Установите зависимости: pip install -r requirements.txt
2. Получите токен бота у @BotFather в Telegram
3. Создайте файл .env и укажите BOT_TOKEN
4. Запустите: python main.py
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Импортируем модули
from database import init_db
from handlers import routers


async def main():
    """
    Главная функция для запуска бота
    """
    # Настраиваем логирование для отслеживания работы бота
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Проверяем наличие токена
    if not BOT_TOKEN:
        print("❌ Ошибка: Токен бота не найден!")
        print("Создайте файл .env и добавьте строку:")
        print('BOT_TOKEN="ваш_токен_здесь"')
        return
    
    # Инициализируем базу данных
    print("🔧 Инициализация базы данных...")
    await init_db()
    
    # Создаем объект бота с токеном
    bot = Bot(token=BOT_TOKEN)
    
    # Создаем диспетчер с хранилищем состояний в памяти
    # MemoryStorage - для хранения состояний FSM (диалогов с пользователем)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрируем все роутеры (обработчики команд)
    print("📝 Регистрация обработчиков...")
    for router in routers:
        dp.include_router(router)
    
    # Удаляем все pending updates и запускаем polling
    # polling - постоянное получение обновлений от Telegram
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("=" * 50)
    print("🤖 Бот запущен и готов к работе!")
    print("=" * 50)
    print("\n📋 Доступные функции:")
    print("  • Добавление задач с категориями и дедлайнами")
    print("  • Назначение ответственных")
    print("  • Изменение статусов (новое, в работе, выполнено)")
    print("  • Фильтрация по категориям")
    print("  • Экспорт в CSV")
    print("\n💡 Команды:")
    print("  /start - Начало работы")
    print("  /add - Добавить задачу")
    print("  /list - Список всех задач")
    print("  /my_tasks - Мои задачи")
    print("  /list_csv - Экспорт в CSV")
    print("\n⏹️  Нажмите Ctrl+C для остановки бота\n")
    
    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    """
    Точка входа в программу
    """
    try:
        # Запускаем основную асинхронную функцию
        asyncio.run(main())
    except KeyboardInterrupt:
        # Обрабатываем прерывание (Ctrl+C)
        print("\n⏹️ Бот остановлен")
