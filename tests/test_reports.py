import unittest
import os
import json
import pandas as pd
from src.reports import spending_by_category


class TestSpendingByCategory(unittest.TestCase):

    def setUp(self):
        """Initial setup for tests."""
        data = [
            {"Дата операции": "2021-11-01 12:30:00",
             "Категория": "Супермаркеты",
             "Сумма операции с округлением": 120.0},
            {"Дата операции": "2021-11-05 12:30:00",
             "Категория": "Супермаркеты",
             "Сумма операции с округлением": 80.0},
            {"Дата операции": "2021-11-10 12:30:00",
             "Категория": "Рестораны",
             "Сумма операции с округлением": 50.0}
        ]
        self.transactions_df = pd.DataFrame(data)
        self.transactions_df['Дата операции'] = pd.to_datetime(self.transactions_df['Дата операции'], dayfirst=True)

        # Use absolute path
        self.generated_filename = os.path.abspath(os.path.join('data', 'spending_by_category_report.json'))

    def test_spending_by_category(self):
        """Test the spending_by_category function and report generation."""
        category = "Супермаркеты"
        date = '2021-12-31'

        expected_result = {
            "category": category,
            "total_spending": 200.0,  # 120.0 + 80.0
            "period": {
                "start_date": "2021-10-02",
                "end_date": "2021-12-31"
            }
        }

        result = spending_by_category(self.transactions_df, category, date)

        self.assertEqual(result, expected_result, "The result dictionary does not match the expected result.")

        self.assertTrue(os.path.isfile(self.generated_filename), "The report JSON file was not created.")

        with open(self.generated_filename, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
            self.assertEqual(file_content, expected_result,
                             "The content of the JSON file does not match the expected result.")

    def tearDown(self):
        """Clean up any resources or files created during tests."""
        if os.path.isfile(self.generated_filename):
            os.remove(self.generated_filename)


if __name__ == '__main__':
    unittest.main()