import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.utils import (get_card_data, get_currency_rates, get_greeting, get_stock_prices, get_top_transactions,
                       get_transactions_from_start_month, load_user_settings)


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """Fixture with test transaction data."""
    return pd.DataFrame(
        {
            "Дата операции": [
                datetime(2023, 10, 15, 12, 0),
                datetime(2023, 9, 20, 10, 0),
                datetime(2023, 10, 1, 8, 0),
            ],
            "hour": [12, 10, 8],
            "Номер карты": ["1234567890123456", "1234567890123456", "9876543210987654"],
            "Сумма операции": [-1000, -500, -2000],
            "Кэшбэк": [10, 5, 20],
            "Категория": ["Супермаркеты", "Кафе", "Транспорт"],
            "Описание": ["Покупка", "Обед", "Такси"],
        }
    )


@pytest.fixture
def mock_settings_file(tmp_path: Path) -> Path:
    """Fixture with temporary settings file."""
    settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "MSFT"]}
    file_path = tmp_path / "user_settings.json"
    with open(file_path, "w") as f:
        json.dump(settings, f)
    return file_path


def test_get_transactions_from_start_month(sample_transactions: pd.DataFrame) -> None:
    """Test of transaction filtering since the beginning of the month."""
    end_date = "2023-10-15 23:59:59"
    result = get_transactions_from_start_month(sample_transactions, end_date)
    assert len(result) == 1
    assert all(result["Дата операции"].dt.month == 10)


def test_get_greeting(sample_transactions: pd.DataFrame) -> None:
    """Testing the function of receiving greetings."""
    greeting = get_greeting(sample_transactions)
    assert greeting in ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]


def test_get_card_data(sample_transactions: pd.DataFrame) -> None:
    """Test of data grouping by maps."""
    result = get_card_data(sample_transactions)
    assert len(result) == 2
    assert all("last_digits" in item for item in result)
    assert all("total_spent" in item for item in result)
    assert all("cashback" in item for item in result)


def test_get_top_transactions(sample_transactions: pd.DataFrame) -> None:
    """Test of getting top 5 transactions."""
    date_time = datetime(2023, 10, 16)
    result = get_top_transactions(sample_transactions, date_time)
    assert len(result) <= 5
    assert all("Дата операции" in item for item in result)
    assert all("Сумма операции" in item for item in result)


def test_load_user_settings(mock_settings_file: Path) -> None:
    """Test loading settings from file."""
    result = load_user_settings(str(mock_settings_file))
    assert isinstance(result, dict)
    assert "user_currencies" in result
    assert "user_stocks" in result


@patch("src.utils.requests.get")
@patch("src.utils.load_user_settings")
@patch.dict("os.environ", {"API_KEY_CURRENCY": "test_key"})
def test_get_currency_rates(mock_load_settings: MagicMock, mock_get: MagicMock, mock_settings_file: Path) -> None:
    """Test for receiving exchange rates."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rate": 0.011}
    mock_get.return_value = mock_response

    # Mock loading settings
    mock_load_settings.return_value = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "MSFT"]}

    result = get_currency_rates()
    assert isinstance(result, list)
    if result:  # Если API вернуло данные
        assert all("symbol" in item for item in result)
        assert all("rate" in item for item in result)


@patch("src.utils.requests.get")
@patch("src.utils.load_user_settings")
@patch.dict("os.environ", {"API_KEY_STOCK": "test_key"})
def test_get_stock_prices(mock_load_settings: MagicMock, mock_get: MagicMock, mock_settings_file: Path) -> None:
    """Stock Price Retrieval Test."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Global Quote": {"01. symbol": "AAPL", "05. price": "150.50"}}
    mock_get.return_value = mock_response

    # Mock loading settings
    mock_load_settings.return_value = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "MSFT"]}

    result = get_stock_prices()
    assert isinstance(result, list)
    if result:  # Если API вернуло данные
        assert all("stock" in item for item in result)
        assert all("price" in item for item in result)


def test_get_greeting_time_ranges() -> None:
    """Test of greeting detection for different time ranges."""
    test_data = [(6, "Доброе утро"), (12, "Добрый день"), (18, "Добрый вечер"), (0, "Доброй ночи")]

    for hour, expected in test_data:
        test_df = pd.DataFrame({"hour": [hour]})
        assert get_greeting(test_df) == expected


def test_get_top_transactions_empty(sample_transactions: pd.DataFrame) -> None:
    """Test getting top transactions for empty result."""
    date_time = datetime(2020, 1, 1)  # Date before all transactions
    result = get_top_transactions(sample_transactions, date_time)
    assert len(result) == 0
