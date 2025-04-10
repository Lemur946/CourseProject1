import logging
import os
import requests
import json
from datetime import datetime
from typing import List, Dict, Any
from read_operations_xlsx import read_transactions_from_excel
from dotenv import load_dotenv

# Setting up a basic configuration for logger
logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
logger = logging.getLogger('utils')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(logs_dir, 'utils.log'), mode='w')
file_formatter = logging.Formatter('%(asctime)s %(filename)s %(levelname)s: %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

file_path_XLSX = '../data/operations.xlsx'
transactions_data = read_transactions_from_excel(file_path_XLSX)

# Load environment variables from .env file
load_dotenv()


def get_greeting(date_time: datetime) -> str:
    """
    Receiving greetings depending on the time of day.
    """
    hour = date_time.hour
    greeting = ""
    if 6 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 18:
        greeting = "Добрый день"
    elif 18 <= hour < 24:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    logger.debug(f"[DEBUG] Greeting: {greeting}")
    return greeting


def get_card_data(date_time: datetime) -> List[Dict[str, Any]]:
    """
    Obtaining data from maps.
    """
    results = {}
    for transaction in transactions_data:
        card_number = str(transaction['Номер карты'])[-4:]
        if card_number not in results:
            results[card_number] = {
                "last_digits": card_number,
                "total_spent": 0.0,
                "cashback": 0.0
            }

        # Check that the transaction falls within the specified period
        operation_date = datetime.strptime(transaction['Дата операции'], "%d.%m.%Y %H:%M:%S")
        if operation_date <= date_time:
            results[card_number]['total_spent'] += transaction['Сумма операции']
            results[card_number]['cashback'] += transaction['Кэшбэк']
    logger.debug(f"[DEBUG] Card Data: {results}")
    return list(results.values())


def get_top_transactions(date_time: datetime) -> List[Dict[str, Any]]:
    """
    Getting top 5 transactions by payment amount.
    """
    transactions = []
    for transaction in transactions_data:
        # Check that the transaction falls within the specified period
        operation_date = datetime.strptime(transaction['Дата операции'], "%d.%m.%Y %H:%M:%S")
        if operation_date <= date_time:
            transactions.append({
                "date": transaction['Дата операции'],
                "amount": transaction['Сумма операции'],
                "category": transaction['Категория'],
                "description": transaction['Описание']
            })

    # Sort transactions and select top 5
    transactions_sorted = sorted(transactions, key=lambda x: abs(x["amount"]), reverse=True)[:5]
    logger.debug(f"[DEBUG] Top Transactions: {transactions_sorted}")
    return transactions_sorted


def load_user_settings(file_path: str) -> Dict[str, List[str]]:
    """
    Loading user settings from a JSON file.
    """
    with open(file_path, 'r') as file:
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
                currency_rates.append({
                    "symbol": target_currency,
                    "rate": data["rate"]
                })
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
                    stock_prices.append({
                        "stock": price_data.get("01. symbol", "N/A"),
                        "price": float(price_data.get("05. price", 0))
                    })
                else:
                    logger.info(f"[INFO] No data received for symbol: {symbol}")
            else:
                logger.error(f"[ERROR] Failed to fetch data for {symbol}. HTTP Status: {response.status_code}")
        except Exception as e:
            logger.error(f"[ERROR] Exception occurred for symbol {symbol}: {str(e)}")

    return stock_prices
