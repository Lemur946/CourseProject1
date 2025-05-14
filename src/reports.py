import json
import logging
import os
from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd


def report_to_file(filename: Optional[str] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            result = func(*args, **kwargs)

            # Generate a file name if it is not passed
            if not filename:
                base_name = func.__name__

                file_name = f"{base_name}_report.json"
            else:
                file_name = filename

            # Determine the path to the data directory
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            os.makedirs(data_dir, exist_ok=True)  # Create the directory if it doesn't exist
            file_path = os.path.join(data_dir, file_name)
            print(f"Writing report to: {file_path}")

            # Write the result to a file
            if isinstance(result, pd.DataFrame):
                result.to_json(file_path, orient="records", lines=True, force_ascii=False, indent=4)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)

            return result

        return wrapper

    return decorator


# Setting up a basic configuration for logger
logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(logs_dir, "reports.log"), mode="w")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


@report_to_file()  # Using decorator without parameters
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Return spending for the given category for the last three months from the provided date.
    """

    # Use current date if not passed
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%Y.%m.%d")

    logger.info(f"Calculating spending for category '{category}' ending at {end_date.strftime('%Y-%m-%d')}")

    # Calculate the beginning of the period (three months ago)
    start_date = end_date - pd.DateOffset(months=3)

    # Filter transactions by date and category
    mask = (
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
        & (transactions["Категория"] == category)
        & (transactions["Сумма операции"] < 0)
    )
    filtered_transactions = transactions.loc[mask]

    # Summarize expenses by category
    total_spending = filtered_transactions["Сумма операции"].sum()

    logger.info(f"Total spending for category '{category}': {total_spending}")

    return filtered_transactions
