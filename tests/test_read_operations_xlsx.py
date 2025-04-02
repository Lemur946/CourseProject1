import unittest
from typing import Any, Dict, Hashable, List
from unittest.mock import Mock, patch

import pandas as pd

from src.read_operations_xlsx import read_transactions_from_excel


class TestReadTransactionsFromExcel(unittest.TestCase):
    """
    Test suite for the read_transactions_from_excel function.
    """

    @patch('pandas.read_excel', side_effect=FileNotFoundError)
    def test_file_not_found(self, mock_read_excel: Mock) -> None:
        """
        Test that the function returns an empty list when the file is not found.
        """
        result: List[Dict[Hashable, Any]] = read_transactions_from_excel('non_existent_file.xlsx')
        self.assertEqual(result, [])
        mock_read_excel.assert_called_once()

    @patch('pandas.read_excel', side_effect=IOError)
    def test_io_error(self, mock_read_excel: Mock) -> None:
        """
        Test that the function returns an empty list on IOError.
        """
        result: List[Dict[Hashable, Any]] = read_transactions_from_excel('io_error_file.xlsx')
        self.assertEqual(result, [])
        mock_read_excel.assert_called_once()

    @patch('pandas.read_excel', side_effect=ValueError)
    def test_value_error(self, mock_read_excel: Mock) -> None:
        """
        Test that the function returns an empty list on ValueError.
        """
        result: List[Dict[Hashable, Any]] = read_transactions_from_excel('corrupted_file.xlsx')
        self.assertEqual(result, [])
        mock_read_excel.assert_called_once()

    @patch('pandas.read_excel')
    def test_empty_file(self, mock_read_excel: Mock) -> None:
        """
        Test that the function returns an empty list for an empty Excel file.
        """
        mock_read_excel.return_value = pd.DataFrame()
        result: List[Dict[Hashable, Any]] = read_transactions_from_excel('empty.xlsx')
        self.assertEqual(result, [])
        mock_read_excel.assert_called_once()

    @patch('pandas.read_excel')
    def test_valid_excel(self, mock_read_excel: Mock) -> None:
        """
        Test that the function correctly processes a valid Excel file
        and returns the expected data as a list of dictionaries.
        """
        # Creating a mock DataFrame
        mock_data: Dict[Hashable, List[Any]] = {
            'name': ['Jane Doe', 'John Doe'],
            'amount': [100.0, 200.0],
            'date': ['2023-01-01', '2023-01-02']
        }
        mock_df = pd.DataFrame(mock_data)

        mock_read_excel.return_value = mock_df
        result: List[Dict[Hashable, Any]] = read_transactions_from_excel('valid.xlsx')
        expected: List[Dict[Hashable, Any]] = [
            {'name': 'Jane Doe', 'amount': 100.0, 'date': '2023-01-01'},
            {'name': 'John Doe', 'amount': 200.0, 'date': '2023-01-02'}
        ]
        self.assertEqual(result, expected)
        mock_read_excel.assert_called_once()
