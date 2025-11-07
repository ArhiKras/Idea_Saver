"""
Модуль для экспорта задач в CSV формат
"""

import csv
from typing import List, Tuple


async def export_tasks_to_csv(tasks: List[Tuple], filename: str = "tasks.csv") -> str:
    """
    Экспорт списка задач в CSV файл
    
    Args:
        tasks: Список задач (кортежи из БД)
        filename: Имя файла для сохранения
    
    Returns:
        Путь к созданному файлу
    """
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        # Создаем writer для записи в CSV
        writer = csv.writer(csvfile)
        
        # Записываем заголовки с новыми полями
        writer.writerow([
            'ID',
            'Задача',
            'Статус',
            'Категория',
            'Дедлайн',
            'Создатель',
            'Ответственный',
            'Дата создания'
        ])
        
        # Записываем данные задач
        for task in tasks:
            # task = (id, text, status, category, deadline, creator, assignee, created_at)
            writer.writerow([
                task[0],  # ID
                task[1],  # Задача
                task[2],  # Статус
                task[3],  # Категория
                task[4] if task[4] else 'Не указан',  # Дедлайн
                task[5],  # Создатель
                task[6] if task[6] else 'Не назначен',  # Ответственный
                task[7]   # Дата создания
            ])
    
    return filename

