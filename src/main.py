import json
from typing import Any, Dict

import pandas as pd

from src.read_operations_xlsx import file_path_XLSX, read_transactions_from_excel
from src.services import analyze_cashback_categories
from src.views import main_view


def to_serializable(val: Any) -> Any:
    """Convert non-serializable data types to serializable."""
    if isinstance(val, pd.Timestamp):
        return val.isoformat()
    if isinstance(val, pd.DataFrame):  # Добавляем обработку для DataFrame
        return val.to_dict(orient="records")  # Преобразуем DataFrame в список словарей
    raise TypeError(f"Object of type {type(val).__name__} is not JSON serializable")


def run_all_functions() -> None:
    """
    The function that starts the work of the entire project
    """

    # Executing the main_view function
    main_view_result: Dict[str, Any] = main_view("2021-12-19 12:00:00")
    print("Результат main_view:")
    print(json.dumps(main_view_result, ensure_ascii=False, indent=4, default=to_serializable))
    print("\n")

    # Loading data from Excel
    transactions_data = read_transactions_from_excel(file_path_XLSX)
    transactions_df = pd.DataFrame(transactions_data)

    # Make sure the transaction date is in datetime format
    transactions_df["Дата операции"] = pd.to_datetime(transactions_df["Дата операции"], dayfirst=True)

    # Performing cashback analysis
    year: int = 2021
    month: int = 11
    cashback_result = analyze_cashback_categories(transactions_data, year, month)
    print("Анализ категорий кэшбэка за 2021.11:")
    print(json.dumps(cashback_result, ensure_ascii=False, indent=4, default=to_serializable))
    print("\n")


if __name__ == "__main__":
    run_all_functions()
