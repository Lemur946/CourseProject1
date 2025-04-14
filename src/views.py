from datetime import datetime
from typing import Any, Dict

import pandas as pd

from src.utils import (get_card_data, get_currency_rates, get_greeting, get_stock_prices, get_top_transactions,
                       get_transactions_from_start_month)


def main_view(input_date: str) -> Dict[str, Any]:
    """The main function for generating a JSON res"""
    # Reading data from Excel
    df_all_transactions = pd.read_excel("../data/operations.xlsx")
    df_all_transactions["Дата операции"] = pd.to_datetime(df_all_transactions["Дата операции"], dayfirst=True)

    # We receive data for the required period
    only_in_period_transactions = get_transactions_from_start_month(df_all_transactions, input_date)

    # Extract the hour from `input_date` and create a DataFrame for the `get_greeting` function
    date_time = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
    df_greeting = pd.DataFrame({"hour": [date_time.hour]})

    # We receive information on cards and top transactions
    greeting = get_greeting(df_greeting)
    cards = get_card_data(only_in_period_transactions)
    top_transactions = get_top_transactions(only_in_period_transactions, date_time)
    currency_rates = get_currency_rates()
    stock_prices = get_stock_prices()

    # Generate a JSON response
    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return result


if __name__ == "__main__":
    result = main_view("2021-12-07 05:02:09")
    print(result)
