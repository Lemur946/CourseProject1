import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Hashable, List

import pandas as pd
import requests
from dotenv import load_dotenv

from src.read_operations_xlsx import read_transactions_from_excel

# Setting up a basic configuration for logger
logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(logs_dir, "utils.log"), mode="w")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

file_path_XLSX = "../data/operations.xlsx"
transactions_data = read_transactions_from_excel(file_path_XLSX)

# Load environment variables from .env file
load_dotenv()


def get_transactions_from_start_month(df: pd.DataFrame, end_date: str) -> pd.DataFrame:
    # Convert a string date to a datetime object
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    # Find the beginning of the month
    start_datetime = end_datetime.replace(day=1)
    # Filter DataFrame by date
    filtered_df = df[(df["Дата операции"] >= start_datetime) & (df["Дата операции"] <= end_datetime)]
    return filtered_df


def get_greeting(df: pd.DataFrame) -> Any:
    """
    Receiving greetings depending on the time of day.
    """

    # We define the greeting rule depending on the time of day
    def determine_greeting(hour: int) -> Any:
        if 6 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 18:
            return "Добрый день"
        elif 18 <= hour < 24:
            return "Добрый вечер"
        else:
            return "Доброй ночи"

    # Apply the rule to determine the greeting
    df["greeting"] = df["hour"].apply(determine_greeting)

    greeting = df["greeting"].iloc[0]

    logger.debug(f"[DEBUG] Greeting: {greeting}")
    return greeting


def get_card_data(df: pd.DataFrame) -> list[dict[Hashable, Any]]:
    """
    Obtaining data from maps.
    """
    df = df.copy()
    df.loc[:, "last_digits"] = df["Номер карты"].astype(str).str[-4:]

    # Group transactions by the last 4 digits of the card number and sum up the expenses and cashback
    aggregated_data = (
        df.groupby("last_digits").agg(total_spent=("Сумма операции", "sum"), cashback=("Кэшбэк", "sum")).reset_index()
    )
    # Convert the result into a list of dictionaries
    results = aggregated_data.to_dict(orient="records")

    return results


def get_top_transactions(df: pd.DataFrame, date_time: datetime) -> list[dict[Hashable, Any]]:
    """
    Getting top 5 transactions by payment amount.
    """
    # Filter transactions that fall within the specified period
    df = df.copy()
    df.loc["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%Y-%m-%d %H:%M:%S")
    filtered_transactions = df[df["Дата операции"] <= date_time]

    # Sort by absolute value of transaction amount and select first 5
    top_transactions = filtered_transactions.sort_values(by="Сумма операции", key=abs, ascending=False).head(5)

    # Convert the result to a list of dictionaries
    results = top_transactions[["Дата операции", "Сумма операции", "Категория", "Описание"]].to_dict(orient="records")

    return results


def load_user_settings(file_path: str) -> Any:
    """
    Loading user settings from a JSON file.
    """
    with open(file_path, "r") as file:
        settings = json.load(file)
    return settings


def get_currency_rates() -> List[Dict[str, Any]]:
    """
    Obtaining exchange rates for selected currency pairs.
    """
    load_dotenv()
    settings = load_user_settings("../data/user_settings.json")
    target_currencies = settings.get("user_currencies", [])
    base_currency = "RUB"
    api_key = os.getenv("API_KEY_CURRENCY")

    currency_rates = []
    for target_currency in target_currencies:
        symbol = f"{target_currency}/{base_currency}"
        url = f"https://api.twelvedata.com/exchange_rate?symbol={symbol}&apikey={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "rate" in data:
                currency_rates.append({"symbol": target_currency, "rate": data["rate"]})
        else:
            logger.error(f"[ERROR] Failed to fetch data for {symbol}. HTTP Status: {response.status_code}")

    return currency_rates


def get_stock_prices() -> List[Dict[str, Any]]:
    """
    Get current stock prices in the required JSON format.
    """
    load_dotenv()
    api_key = os.getenv("API_KEY_STOCK")
    if not api_key:
        logger.error("[ERROR] API_KEY_STOCK is not set.")
        return []

    settings = load_user_settings("../data/user_settings.json")
    symbols = settings.get("user_stocks", [])

    stock_prices = []
    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()
                price_data = response_data.get("Global Quote", {})
                if price_data:
                    stock_prices.append(
                        {"stock": price_data.get("01. symbol", "N/A"), "price": float(price_data.get("05. price", 0))}
                    )
                else:
                    logger.info(f"[INFO] No data received for symbol: {symbol}")
            else:
                logger.error(f"[ERROR] Failed to fetch data for {symbol}. HTTP Status: {response.status_code}")
        except Exception as e:
            logger.error(f"[ERROR] Exception occurred for symbol {symbol}: {str(e)}")

    return stock_prices
