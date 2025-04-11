from datetime import datetime
from typing import Any, Dict

from src.utils import get_card_data, get_currency_rates, get_greeting, get_stock_prices, get_top_transactions


def main_view(input_date: str) -> Dict[str, Any]:
    """
    The main function for generating a JSON response.
    """
    try:
        date_time = datetime.strptime(input_date, "%Y.%m.%d")
    except ValueError as e:
        return {"error": str(e)}

    # Receive data
    greeting = get_greeting(date_time)
    cards = get_card_data(date_time)
    top_transactions = get_top_transactions(date_time)
    currency_rates = get_currency_rates()
    stock_prices = get_stock_prices()

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
