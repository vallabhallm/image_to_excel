"""Test Excel generator module."""
import os
import pytest
import pandas as pd
from unittest.mock import patch, Mock, mock_open
from src.generators.excel_generator import ExcelGenerator

@pytest.fixture
def generator():
    """Excel generator fixture."""
    return ExcelGenerator()

def test_clean_sheet_name(generator):
    """Test clean_sheet_name method."""
    assert generator.clean_sheet_name("Test") == "Test"
    assert generator.clean_sheet_name("Test[1]") == "Test1"
    assert generator.clean_sheet_name("Test:1") == "Test1"
    assert generator.clean_sheet_name("Test*1") == "Test1"
    assert generator.clean_sheet_name("Test?1") == "Test1"
    assert generator.clean_sheet_name("Test/1") == "Test1"
    assert generator.clean_sheet_name("Test\\1") == "Test1"
    assert generator.clean_sheet_name("A" * 40) == "A" * 31
    assert generator.clean_sheet_name("") == "Sheet1"
    assert generator.clean_sheet_name(None) == "Sheet1"

def test_create_excel_success(generator):
    """Test create_excel success."""
    with patch('pandas.ExcelWriter') as mock_writer, \
         patch('os.makedirs') as mock_makedirs, \
         patch('pandas.DataFrame') as mock_df:
        # Mock the DataFrame instance
        df_instance = Mock()
        mock_df.return_value = df_instance
        
        # Set up test data
        data = {
            "Sheet1": [
                {
                    "invoice_number": "INV-001",
                    "invoice_date": "2025-04-01",
                    "vendor": "Test Vendor",
                    "customer": "Test Customer",
                    "total_amount": 100.0,
                    "currency": "USD",
                    "payment_terms": "Net 30",
                    "items": [
                        {
                            "description": "Test Item",
                            "quantity": 1,
                            "unit_price": 100.0,
                            "amount": 100.0
                        }
                    ]
                }
            ],
            "Sheet2": [
                {
                    "raw_text": "Sample raw invoice text"
                }
            ],
            "Sheet3": [
                {
                    "content": "Legacy content format"
                }
            ],
            "EmptySheet": []
        }
        
        # Call the method
        result = generator.create_excel(data, "test.xlsx")
        
        # Check results
        assert result is True
        mock_makedirs.assert_not_called()  # No directory in the path
        mock_df.call_count == 3  # Called for each non-empty sheet
        df_instance.to_excel.call_count == 3  # Called for each non-empty sheet

def test_create_excel_with_directory(generator):
    """Test create_excel with directory."""
    with patch('pandas.ExcelWriter') as mock_writer, \
         patch('os.makedirs') as mock_makedirs, \
         patch('pandas.DataFrame') as mock_df:
        # Mock the DataFrame instance
        df_instance = Mock()
        mock_df.return_value = df_instance
        
        # Set up test data
        data = {
            "Sheet1": [
                {
                    "invoice_number": "INV-001",
                    "invoice_date": "2025-04-01",
                    "vendor": "Test Vendor",
                    "customer": "Test Customer"
                }
            ]
        }
        
        # Call the method
        result = generator.create_excel(data, "test/output.xlsx")
        
        # Check results
        assert result is True
        mock_makedirs.assert_called_once_with("test", exist_ok=True)
        df_instance.to_excel.assert_called_once()

def test_create_excel_no_data(generator):
    """Test create_excel with no data."""
    result = generator.create_excel({}, "test.xlsx")
    assert result is False

def test_create_excel_only_empty_sheets(generator):
    """Test create_excel with only empty sheets."""
    with patch('pandas.ExcelWriter') as mock_writer:
        data = {
            "Sheet1": [],
            "Sheet2": []
        }
        result = generator.create_excel(data, "test.xlsx")
        assert result is False

def test_create_excel_duplicate_sheet_names(generator):
    """Test create_excel with duplicate sheet names."""
    with patch('pandas.ExcelWriter') as mock_writer, \
         patch('pandas.DataFrame') as mock_df:
        # Mock the DataFrame instance
        df_instance = Mock()
        mock_df.return_value = df_instance
        
        # Set up test data with duplicate sheet names
        data = {
            "Sheet": [
                {"invoice_number": "INV-001"}
            ],
            "Sheet[1]": [
                {"invoice_number": "INV-002"}
            ]
        }
        
        # Call the method
        result = generator.create_excel(data, "test.xlsx")
        
        # Check results
        assert result is True
        assert mock_df.call_count == 2  # Called for each sheet
        assert df_instance.to_excel.call_count == 2  # Called for each sheet

def test_create_excel_error(generator):
    """Test create_excel with error."""
    with patch('pandas.ExcelWriter', side_effect=Exception("Test error")):
        data = {
            "Sheet1": [
                {"invoice_number": "INV-001"}
            ]
        }
        result = generator.create_excel(data, "test.xlsx")
        assert result is False

def test_line_items_sheet_creation(generator):
    """Test creation of line items sheet."""
    with patch('pandas.ExcelWriter') as mock_writer, \
         patch('pandas.DataFrame') as mock_df:
        # Mock the DataFrame instance
        df_instance = Mock()
        mock_df.return_value = df_instance
        
        # Set up test data with items that should generate a line items sheet
        data = {
            "Invoices": [
                {
                    "invoice_number": "INV-001",
                    "invoice_date": "2025-04-01",
                    "vendor": "Test Vendor",
                    "items": [
                        {
                            "description": "Item 1",
                            "quantity": 2,
                            "unit_price": 10.0,
                            "amount": 20.0
                        },
                        {
                            "description": "Item 2",
                            "quantity": 1,
                            "unit_price": 15.0,
                            "amount": 15.0
                        }
                    ]
                }
            ]
        }
        
        # Call the method
        result = generator.create_excel(data, "test.xlsx")
        
        # Check results
        assert result is True
        assert mock_df.call_count == 2  # One for summary sheet, one for line items
        assert df_instance.to_excel.call_count == 2  # Once for each sheet
