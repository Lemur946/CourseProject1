import json
import logging
from typing import Any, Dict, Hashable, List

import pytest

from src.services import analyze_cashback_categories


# Fixture for test transaction data
@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Fixture with test data of transactions of different months and categories"""
    return [
        {"Дата операции": "15.01.2023 12:00:00", "Категория": "Супермаркеты", "Кэшбэк": 100.5},
        {"Дата операции": "20.01.2023 15:30:00", "Категория": "АЗС", "Кэшбэк": 50.0},
        {"Дата операции": "05.02.2023 09:45:00", "Категория": "Рестораны", "Кэшбэк": 200.0},
        {"Дата операции": "10.01.2023 18:20:00", "Категория": "Супермаркеты", "Кэшбэк": 75.3},
    ]


def test_cashback_sum_calculation(sample_transactions: List[Dict[Hashable, Any]]) -> None:
    """Test of correct calculation of cashback amount by categories"""
    # Call the function for January 2023
    result = analyze_cashback_categories(sample_transactions, 2023, 1)
    parsed_result = json.loads(result)

    # Checking amounts by category
    assert parsed_result["Супермаркеты"] == 175  # 100.5 + 75.3 = 175.8 → int(175.8) = 175
    assert parsed_result["АЗС"] == 50
    assert "Рестораны" not in parsed_result


def test_month_year_filtering(sample_transactions: List[Dict[Hashable, Any]]) -> None:
    """Test filtering transactions by month and year"""
    # Call the function for February 2023
    result = analyze_cashback_categories(sample_transactions, 2023, 2)
    parsed_result = json.loads(result)

    # We check for the presence of February transactions only
    assert len(parsed_result) == 1
    assert parsed_result["Рестораны"] == 200


def test_empty_result_for_no_transactions(sample_transactions: List[Dict[Hashable, Any]]) -> None:
    """Test of handling missing transactions for a period"""
    # Call the function for a non-existent month
    result = analyze_cashback_categories(sample_transactions, 2024, 1)
    parsed_result = json.loads(result)

    assert len(parsed_result) == 0


def test_float_to_int_conversion() -> None:
    """Test of correct conversion of cashback float to int"""
    # Test data with fractional values
    test_data = [
        {"Дата операции": "01.01.2023 00:00:00", "Категория": "Тест", "Кэшбэк": 123.9},  # Should be converted to 123
        {"Дата операции": "02.01.2023 00:00:00", "Категория": "Тест", "Кэшбэк": 456.1},  # Should be converted to 456
    ]
    test_year = 2023
    test_month = 1

    result = analyze_cashback_categories(test_data, test_year, test_month)
    parsed_result = json.loads(result)

    assert parsed_result["Тест"] == 579  # 123 + 456 = 579


def test_logging(caplog: pytest.LogCaptureFixture, sample_transactions: List[Dict[Hashable, Any]]) -> None:
    """Test of correctness of logging of operations"""
    with caplog.at_level(logging.INFO):
        analyze_cashback_categories(sample_transactions, 2023, 1)

    # Check the log entries
    assert "Starting cashback category analysis for 2023-1" in caplog.text
    assert "Completed cashback category calculation for 2023-1" in caplog.text


def test_invalid_date_format(sample_transactions: List[Dict[Hashable, Any]]) -> None:
    """Test for handling incorrect date formats"""
    # We spoil the date format in one element
    sample_transactions[0]["Дата операции"] = "2023-01-15"

    with pytest.raises(ValueError):
        analyze_cashback_categories(sample_transactions, 2023, 1)


def test_missing_keys(sample_transactions: List[Dict[Hashable, Any]]) -> None:
    """Test for handling missing mandatory fields"""
    # Remove the required field
    del sample_transactions[0]["Категория"]

    with pytest.raises(KeyError):
        analyze_cashback_categories(sample_transactions, 2023, 1)
