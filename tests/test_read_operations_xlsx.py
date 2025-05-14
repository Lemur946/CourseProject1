import os
from tempfile import NamedTemporaryFile

import pandas as pd

from src.read_operations_xlsx import read_transactions_from_excel


def test_read_valid_excel() -> None:
    """Test with explicit file closing before reading"""
    try:
        with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            df = pd.DataFrame(
                {
                    "Дата операции": ["2023-10-15"],
                    "Категория": ["Супермаркеты"],
                    "Сумма операции с округлением": [1000.0],
                }
            )
            df.to_excel(tmp.name, index=False, engine="openpyxl")

        # Read after closing the file
        result = read_transactions_from_excel(tmp.name)

        assert len(result) == 1
        assert result[0]["Категория"] == "Супермаркеты"
    finally:
        os.unlink(tmp.name)  # Forced deletion


def test_read_empty_excel() -> None:
    """Test with guaranteed file closure"""
    import os
    from tempfile import NamedTemporaryFile

    try:
        with NamedTemporaryFile(suffix=".xlsx", delete=False, mode="w") as tmp:
            tmp.close()  # Explicit close for Windows
            df = pd.DataFrame()
            df.to_excel(tmp.name, engine="openpyxl")

        result = read_transactions_from_excel(tmp.name)
        assert result == []
    finally:
        os.remove(tmp.name)
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
