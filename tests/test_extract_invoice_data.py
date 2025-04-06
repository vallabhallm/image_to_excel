"""Tests for the extract_invoice_data module."""

import os
import sys
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from src.extract_invoice_data import extract_invoice_data, main


@pytest.fixture
def mock_config():
    """Mock ConfigManager fixture."""
    with patch('src.extract_invoice_data.ConfigManager') as mock_config_class:
        mock_conf = MagicMock()
        mock_conf.get.return_value = "test_api_key"
        mock_config_class.return_value = mock_conf
        yield mock_conf


@pytest.fixture
def mock_parser():
    """Mock GPTInvoiceParser fixture."""
    with patch('src.extract_invoice_data.GPTInvoiceParser') as mock_parser_class:
        mock_p = MagicMock()
        
        # Setup sample DataFrame to be returned by extract_data
        sample_df = pd.DataFrame({
            'qty': [1.0],
            'description': ['Test Item'],
            'invoice_number': ['INV-001'],
            'invoice_date': ['01.01.2025']
        })
        
        mock_p.extract_data.return_value = sample_df
        mock_parser_class.return_value = mock_p
        yield mock_p


def test_extract_invoice_data_success(mock_config, mock_parser):
    """Test extracting data from invoice text successfully."""
    # Call the function
    result = extract_invoice_data("Sample invoice text")
    
    # Verify the result is a DataFrame with expected columns
    assert isinstance(result, pd.DataFrame)
    
    # Check that all expected columns are in the result
    expected_columns = [
        'qty', 'description', 'pack', 'price', 'discount', 'vat', 'invoice_value',
        'invoice_number', 'account_number', 'invoice_date', 'invoice_time',
        'invoice_type', 'handled_by', 'our_ref', 'delivery_no', 'your_ref',
        'supplier_name', 'supplier_address', 'supplier_tel', 'supplier_fax',
        'supplier_email', 'customer_name', 'customer_address', 'goods_value',
        'vat_code', 'vat_rate_percent', 'vat_amount', 'total_amount', 'batch',
        'expiry_date'
    ]
    for col in expected_columns:
        assert col in result.columns
    
    # Check that values from mock parser are present
    assert result['qty'].iloc[0] == 1.0
    assert result['description'].iloc[0] == 'Test Item'
    assert result['invoice_number'].iloc[0] == 'INV-001'
    
    # Verify parser was called with correct text
    mock_parser.extract_data.assert_called_once_with("Sample invoice text")


def test_extract_invoice_data_no_api_key(mock_config):
    """Test extracting data with missing API key."""
    # Setup mock to return None for API key
    mock_config.get.return_value = None
    
    # Call the function
    result = extract_invoice_data("Sample invoice text")
    
    # Verify the result is None due to missing API key
    assert result is None


def test_extract_invoice_data_parser_failure(mock_config, mock_parser):
    """Test extracting data when parser fails."""
    # Setup mock to return None for extract_data
    mock_parser.extract_data.return_value = None
    
    # Call the function
    result = extract_invoice_data("Sample invoice text")
    
    # Verify the result is None due to parser failure
    assert result is None


def test_extract_invoice_data_exception(mock_config):
    """Test extracting data with an exception."""
    # Setup mock to raise an exception
    with patch('src.extract_invoice_data.GPTInvoiceParser') as mock_parser_class:
        mock_parser_class.side_effect = Exception("Test error")
        
        # Call the function
        result = extract_invoice_data("Sample invoice text")
        
        # Verify the result is None due to exception
        assert result is None


def test_main_success(tmp_path, mock_config, mock_parser, monkeypatch):
    """Test main function with successful execution."""
    # Create test input file
    input_file = tmp_path / "test_input.txt"
    input_file.write_text("Sample invoice text")
    
    # Create test output file name
    output_file = tmp_path / "test_output.xlsx"
    
    # Mock sys.argv
    test_args = ["extract_invoice_data.py", str(input_file), str(output_file)]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    # Call the main function
    with patch('builtins.print') as mock_print:
        result = main()
    
    # Verify the result is 0 (success)
    assert result == 0
    
    # Verify the output file was created
    assert os.path.exists(output_file)
    
    # Verify print was called with success message
    mock_print.assert_any_call(f"Successfully extracted invoice data to {output_file}")


def test_main_no_args(monkeypatch):
    """Test main function with no arguments."""
    # Mock sys.argv with no arguments
    monkeypatch.setattr(sys, 'argv', ["extract_invoice_data.py"])
    
    # Call the main function
    with patch('builtins.print') as mock_print:
        result = main()
    
    # Verify the result is 1 (failure)
    assert result == 1
    
    # Verify print was called with usage message
    mock_print.assert_called_with("Usage: python extract_invoice_data.py <input_file> [output_file]")


def test_main_file_not_found(monkeypatch):
    """Test main function with nonexistent input file."""
    # Mock sys.argv with nonexistent file
    monkeypatch.setattr(sys, 'argv', ["extract_invoice_data.py", "nonexistent_file.txt"])
    
    # Call the main function
    result = main()
    
    # Verify the result is 1 (failure)
    assert result == 1


def test_main_parser_failure(tmp_path, mock_config, monkeypatch):
    """Test main function with parser failure."""
    # Create test input file
    input_file = tmp_path / "test_input.txt"
    input_file.write_text("Sample invoice text")
    
    # Mock sys.argv
    test_args = ["extract_invoice_data.py", str(input_file)]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    # Mock extract_invoice_data to return None
    with patch('src.extract_invoice_data.extract_invoice_data', return_value=None):
        # Call the main function
        result = main()
    
    # Verify the result is 1 (failure)
    assert result == 1
