import pytest
import json
from src.services import analyze_cashback_categories


def test_analyze_cashback_categories():
    """Function testing the analyze_cashback_categories function"""
    test_data = [
        {'Дата операции': '15.06.2023 12:30:00', 'Категория': 'Supermarkets', 'Кэшбэк': 5.0},
        {'Дата операции': '20.06.2023 15:45:00', 'Категория': 'Fuel', 'Кэшбэк': 3.5},
        {'Дата операции': '25.06.2023 10:15:00', 'Категория': 'Supermarkets', 'Кэшбэк': 7.0},
        {'Дата операции': '30.06.2023 18:00:00', 'Категория': 'Supermarkets', 'Кэшбэк': float('nan')},
        {'Дата операции': '01.07.2023 12:00:00', 'Категория': 'Supermarkets', 'Кэшбэк': 10.0},
        # Should be ignored as it's in July
    ]

    expected_output = {
        "Supermarkets": 12,  # 5 + 7, игнорирем NaN и транзакции июля
        "Fuel": 3  # округлено до целого числа
    }

    result_json = analyze_cashback_categories(test_data, 2023, 6)

    # Assert that the results match the expected output
    assert json.loads(result_json) == expected_output


if __name__ == "__main__":
    pytest.main()
