import json
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional, Any
from read_operations_xlsx import read_transactions_from_excel, file_path_XLSX


def report_to_file(filename: Optional[str] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Получим результат выполнения функции
            result = func(*args, **kwargs)

            # Формируем имя файла, если оно не передано
            if not filename:
                base_name = func.__name__
                # timestamp = datetime.now().strftime('%Y%m%d')
                file_name = f"{base_name}_report.json"
            else:
                file_name = filename

            # Определяем путь к директории data
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)  # Создаем директорию, если она не существует

            # Полный путь к файлу в директории data
            file_path = os.path.join(data_dir, file_name)
            print(f"Writing report to: {file_path}")

            # Записываем результат в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            return result

        return wrapper

    return decorator


# Setting up a basic configuration for logger
# Определите директорию логов
logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))

# Создайте директорию, если она не существует
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
logger = logging.getLogger('services')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(logs_dir, 'reports.log'), mode='w')
file_formatter = logging.Formatter('%(asctime)s %(filename)s %(levelname)s: %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


@report_to_file()  # Используем декоратор без параметров
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
    """
    Return spending for the given category for the last three months from the provided date.
    """

    # Используем текущую дату, если не передана
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, '%Y-%m-%d')

    # Логгирование информации о дате отчета
    logger.info(f"Calculating spending for category '{category}' ending at {end_date.strftime('%Y-%m-%d')}")

    # Вычисляем начало периода (три месяца назад)
    start_date = end_date - timedelta(days=90)

    print(f"End date: {end_date}")
    print(f"Start date: {start_date}")

    # Фильтруем транзакции по дате и категории
    mask = (transactions['Дата операции'] >= start_date) & (transactions['Дата операции'] <= end_date) & \
           (transactions['Категория'] == category)
    filtered_transactions = transactions.loc[mask]

    print(f"Filtered transactions: {filtered_transactions}")

    # Суммируем траты по категории
    total_spending = filtered_transactions['Сумма операции с округлением'].sum()

    print(f"Total spending: {total_spending}")

    # Подготовка результата в формате JSON-подобного словаря
    result = {
        "category": category,
        "total_spending": total_spending,
        "period": {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }
    }

    # Логгирование итога расчета
    logger.info(f"Total spending for category '{category}': {total_spending}")

    return result


transactions_list = read_transactions_from_excel(file_path_XLSX)
transactions_df = pd.DataFrame(transactions_list)
transactions_df['Дата операции'] = pd.to_datetime(transactions_df['Дата операции'], dayfirst=True)
category = "Супермаркеты"
date = '2021-12-31'

if __name__ == "__main__":
    spending_by_category(transactions_df, category, date)
