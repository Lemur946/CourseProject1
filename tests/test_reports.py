from datetime import datetime

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """Fixture with test transaction data."""
    data = {
        "Дата операции": ["15.10.2023", "20.09.2023", "05.08.2023", "01.07.2023"],
        "Категория": ["Супермаркеты", "Кафе", "Супермаркеты", "Транспорт"],
        "Сумма операции": [-1000, -500, -800, -300],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    return df


def test_spending_by_category_returns_dataframe(sample_transactions: pd.DataFrame) -> None:
    """Checking that a function returns a DataFrame"""
    result = spending_by_category(transactions=sample_transactions, category="Супермаркеты")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_filtering(sample_transactions: pd.DataFrame) -> None:
    """ПChecking filtering by category and date"""
    result = spending_by_category(transactions=sample_transactions, category="Супермаркеты", date="2023.10.20")

    # Check that only transactions of the required category are returned
    assert all(result["Категория"] == "Супермаркеты")

    # Check that only transactions for the last 3 months are returned
    min_date = datetime(2023, 7, 20)  # 3 месяца от конечной даты
    assert all(result["Дата операции"] >= min_date)


def test_spending_by_category_empty_result(sample_transactions: pd.DataFrame) -> None:
    """Checking for missing transaction handling"""
    result = spending_by_category(transactions=sample_transactions, category="Несуществующая")
    assert len(result) == 0  # Пустой DataFrame


def test_spending_by_category_current_date(sample_transactions: pd.DataFrame) -> None:
    """Checking the work with the current date"""
    result = spending_by_category(transactions=sample_transactions, category="Супермаркеты")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_negative_values(sample_transactions: pd.DataFrame) -> None:
    """Check that only negative values ​​are taken into account"""
    # Add a positive transaction
    positive_trans = pd.DataFrame(
        {"Дата операции": [datetime.now()], "Категория": ["Супермаркеты"], "Сумма операции": [1000]}
    )
    test_data = pd.concat([sample_transactions, positive_trans])

    result = spending_by_category(transactions=test_data, category="Супермаркеты")
    # Check that the positive transaction did not get into the result
    assert all(result["Сумма операции"] < 0)
