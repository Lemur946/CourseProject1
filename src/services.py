import json
import logging
import math
import os
from datetime import datetime
from typing import List, Dict, Any, Hashable
from read_operations_xlsx import read_transactions_from_excel, file_path_XLSX

# Setting up a basic configuration for logger
# Определите директорию логов
logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))

# Создайте директорию, если она не существует
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
logger = logging.getLogger('services')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(logs_dir, 'services.log'), mode='w')
file_formatter = logging.Formatter('%(asctime)s %(filename)s %(levelname)s: %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def analyze_cashback_categories(data: List[Dict[Hashable, Any]], year: int, month: int) -> str:
    """
    Analyzes the most profitable categories for cashback in a given month and year.
    """

    logger.info(f"Starting cashback category analysis for {year}-{month}")

    # Modify the format to match the date format in your excel file
    format_str = '%d.%m.%Y %H:%M:%S'  # Format string for the date in your data

    # Filter transactions for the specified year and month
    filtered_data = filter(lambda x: datetime.strptime(x['Дата операции'], format_str).year == year
                                     and datetime.strptime(x['Дата операции'], format_str).month == month, data)
    # Compute cashback per category
    category_cashback = {}
    for transaction in filtered_data:
        category = transaction['Категория']
        cashback = float(transaction.get('Кэшбэк', 0))

        # Check for NaN and skip if true
        if isinstance(cashback, float) and math.isnan(cashback):
            continue

        cashback = int(cashback)  # Convert to integer

        if category not in category_cashback:
            category_cashback[category] = cashback
        else:
            category_cashback[category] += cashback

    logger.info(f"Completed cashback category calculation for {year}-{month}")

    # Return the result as a JSON string
    return json.dumps(category_cashback, ensure_ascii=False, indent=4)


data = read_transactions_from_excel(file_path_XLSX)

if __name__ == "__main__":
    result_json = analyze_cashback_categories(data, 2021, 11)  # Example for June 2023
    print(result_json)
