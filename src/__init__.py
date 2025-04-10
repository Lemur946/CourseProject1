import json
import pandas as pd
from src.utils import get_card_data, get_top_transactions
from src.views import main_view
from src.reports import spending_by_category
from src.services import analyze_cashback_categories
from read_operations_xlsx import read_transactions_from_excel, file_path_XLSX

def run_all_functions():
    """
    The function that starts the work of the entire project
    """
    # Date to analyze
    analysis_date = '2021.12.31'

    # Executing the main_view function
    main_view_result = main_view('2021.12.19')
    print("Результат main_view:")
    print(json.dumps(main_view_result, ensure_ascii=False, indent=4))
    print("\n")

    # Loading data from Excel
    transactions_data = read_transactions_from_excel(file_path_XLSX)
    transactions_df = pd.DataFrame(transactions_data)

    # Make sure the transaction date is in datetime format
    transactions_df['Дата операции'] = pd.to_datetime(transactions_df['Дата операции'], dayfirst=True)

    # Performing an analysis of expenses by category
    category = "Супермаркеты"
    spending_result = spending_by_category(transactions_df, category, analysis_date)
    print(f"Расходы по категории '{category}':")
    print(json.dumps(spending_result, ensure_ascii=False, indent=4))
    print("\n")

    # Performing cashback analysis
    year = 2021
    month = 11
    cashback_result = analyze_cashback_categories(transactions_data, year, month)
    print("Анализ категорий кэшбэка за 2021.11:")
    print(cashback_result)
    print("\n")

if __name__ == "__main__":
    run_all_functions()