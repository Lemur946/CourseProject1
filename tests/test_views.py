import pytest
from src.views import main_view

def test_main_view():
    result = main_view("2021-12-21 10:00:00")
    assert result["greeting"] in ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result

    # Проверка, что данные по картам содержат ключи last_digits, total_spent, cashback
    assert all("last_digits" in card for card in result["cards"])
    assert all("total_spent" in card for card in result["cards"])
    assert all("cashback" in card for card in result["cards"])

    # Проверка, что top_transactions содержат ключи date, amount, category, description
    assert all("date" in transaction for transaction in result["top_transactions"])
    assert all("amount" in transaction for transaction in result["top_transactions"])
    assert all("category" in transaction for transaction in result["top_transactions"])
    assert all("description" in transaction for transaction in result["top_transactions"])

    # Проверка, что currency_rates и stock_prices содержат необходимые поля
    assert all("currency" in rate and "rate" in rate for rate in result["currency_rates"])
    assert all("stock" in price and "price" in price for price in result["stock_prices"])
