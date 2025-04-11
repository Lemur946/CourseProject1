import json
import unittest
from datetime import datetime
from typing import Any
from unittest.mock import mock_open, patch

import pytest

from src.utils import get_currency_rates, get_greeting, get_stock_prices, load_user_settings

SAMPLE_TRANSACTIONS = [
    {
        'Номер карты': '1234567890123456',
        'Дата операции': '15.01.2023 12:00:00',
        'Сумма операции': 1000.0,
        'Кэшбэк': 50.0,
        'Категория': 'Супермаркеты',
        'Описание': 'Покупки'
    },
    {
        'Номер карты': '9876543210987654',
        'Дата операции': '20.01.2023 15:30:00',
        'Сумма операции': 5000.0,
        'Кэшбэк': 250.0,
        'Категория': 'АЗС',
        'Описание': 'Заправка'
    }
]


@pytest.fixture(autouse=True)
def setup_mocks(monkeypatch: Any) -> None:
    """Global fixture for all mocks"""
    # Mock transaction data
    monkeypatch.setattr('utils.transactions_data', SAMPLE_TRANSACTIONS)

    # Mock for loading settings
    settings_mock = mock_open(read_data=json.dumps({
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL"]
    }))
    monkeypatch.setattr("builtins.open", settings_mock)

    # Mock for environment variables
    monkeypatch.setenv("API_KEY_CURRENCY", "test_key")
    monkeypatch.setenv("API_KEY_STOCK", "test_key")


class TestGetGreeting(unittest.TestCase):
    def test_morning_greeting(self) -> None:
        date_time = datetime(2023, 10, 1, 8, 0)  # 08:00 AM
        self.assertEqual(get_greeting(date_time), "Доброе утро")

    def test_afternoon_greeting(self) -> None:
        date_time = datetime(2023, 10, 1, 14, 0)  # 02:00 PM
        self.assertEqual(get_greeting(date_time), "Добрый день")

    def test_evening_greeting(self) -> None:
        date_time = datetime(2023, 10, 1, 19, 0)  # 07:00 PM
        self.assertEqual(get_greeting(date_time), "Добрый вечер")

    def test_night_greeting(self) -> None:
        date_time = datetime(2023, 10, 1, 2, 0)  # 02:00 AM
        self.assertEqual(get_greeting(date_time), "Доброй ночи")

    def test_midnight_greeting(self) -> None:
        date_time = datetime(2023, 10, 1, 0, 0)  # 12:00 AM
        self.assertEqual(get_greeting(date_time), "Доброй ночи")

    def test_last_minute_of_night_greeting(self) -> None:
        date_time = datetime(2023, 10, 1, 5, 59)  # 05:59 AM
        self.assertEqual(get_greeting(date_time), "Доброй ночи")


# Tests for API requests
@patch('utils.requests.get')
def test_currency_rates_success(mock_get: Any) -> None:
    """Test of getting exchange rates with mock API"""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"rate": 75.5}

    result = get_currency_rates()

    assert len(result) == 2  # USD and EUR from mock settings
    assert any(r['symbol'] == 'USD' for r in result)
    assert mock_get.call_count == 2


@patch('utils.requests.get')
def test_stock_prices_error(mock_get: Any, caplog: Any) -> None:
    """Test for handling errors when requesting shares"""
    mock_get.return_value.status_code = 500

    result = get_stock_prices()

    assert len(result) == 0
    assert "HTTP Status: 500" in caplog.text


def test_load_user_settings() -> None:
    """Test loading settings from file"""
    with patch("builtins.open", mock_open(read_data='{"test": "data"}')):
        result = load_user_settings("dummy_path")
        assert result == {"test": "data"}
