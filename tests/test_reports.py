from typing import Any, Dict

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """Фикстура с тестовыми данными транзакций."""
    data = {
        'Дата операции': ['15.10.2023', '20.09.2023', '05.08.2023', '01.07.2023'],
        'Категория': ['Супермаркеты', 'Кафе', 'Супермаркеты', 'Транспорт'],
        'Сумма операции с округлением': [1000, 500, 800, 300]
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
    return df


def test_spending_by_category_period(sample_transactions: pd.DataFrame) -> None:
    """Тестирование расчета расходов за период."""
    result: Dict[str, Any] = spending_by_category(
        transactions=sample_transactions,
        category="Супермаркеты",
        date="2023.10.20"
    )

    # Проверка периода
    assert result['period']['start_date'] == '2023.07.22'
    assert result['period']['end_date'] == '2023.10.20'

    # Проверка суммы: 1000 + 800 = 1800
    assert result['total_spending'] == 1800


def test_spending_by_category_empty(sample_transactions: pd.DataFrame) -> None:
    """Тестирование обработки отсутствия транзакций в категории."""
    result: Dict[str, Any] = spending_by_category(
        transactions=sample_transactions,
        category="Несуществующая",
        date="2023.10.20"
    )

    assert result['total_spending'] == 0
