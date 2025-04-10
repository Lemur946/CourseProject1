from datetime import datetime
from typing import Dict, Any
from utils import (
    get_greeting,
    get_card_data,
    get_top_transactions,
    get_currency_rates,
    get_stock_prices
)


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
        "stock_prices": stock_prices
    }


if __name__ == "__main__":
    print(main_view('2021.12.19'))
