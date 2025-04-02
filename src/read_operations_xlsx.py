from typing import Any, Hashable

import pandas as pd


def read_transactions_from_excel(file_path_XLSX: str) -> list[dict[Hashable, Any]]:
    """
    A function that reads financial transactions from an Excel file.
    """
    try:

        df = pd.read_excel(file_path_XLSX)  # Open the Excel file and read the contents
        if df.empty:  # Checking if a file is empty
            return []
        return df.to_dict(orient='records')
    except FileNotFoundError:
        print(f"File not found: {file_path_XLSX}")
        return []
    except IOError:
        print(f"I/O error while working with file: {file_path_XLSX}")
        return []
    except ValueError:
        print(f"Error processing Excel file: {file_path_XLSX}")
        return []


file_path_XLSX = '../data/operations.xlsx'
data = read_transactions_from_excel(file_path_XLSX)
