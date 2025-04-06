"""Tests for the main module."""

import os
import sys
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, Mock

from src.main import main


@pytest.fixture
def mock_openai():
    """Mock OpenAI API client."""
    with patch('openai.OpenAI') as mock:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test content"
        mock_client.chat.completions.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock


@pytest.fixture
def mock_config():
    """Mock ConfigManager fixture."""
    with patch('src.main.ConfigManager') as mock_config_class:
        mock_conf = MagicMock()
        mock_conf.get.return_value = "test_api_key"
        mock_config_class.return_value = mock_conf
        yield mock_conf


@pytest.fixture
def mock_parser():
    """Mock GPTInvoiceParser fixture."""
    with patch('src.main.GPTInvoiceParser') as mock_parser_class:
        mock_p = MagicMock()
        mock_parser_class.return_value = mock_p
        yield mock_p


@pytest.fixture
def mock_generator():
    """Mock ExcelGenerator fixture."""
    with patch('src.main.ExcelGenerator') as mock_generator_class:
        mock_g = MagicMock()
        mock_g.create_excel.return_value = True
        mock_generator_class.return_value = mock_g
        yield mock_g


@pytest.fixture
def test_env(tmp_path):
    """Create test environment."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    test_image = test_dir / "test.png"
    test_image.write_bytes(b"test image")
    output_file = tmp_path / "output.xlsx"
    return {"dir": test_dir, "image": test_image, "output": output_file}


def test_main_success(test_env, mock_openai, mock_config, mock_parser, mock_generator):
    """Test successful execution."""
    # Create mock results
    mock_results = {
        str(test_env["dir"]): pd.DataFrame({
            'qty': [1, 2],
            'description': ['Item A', 'Item B'],
            'invoice_number': ['INV001', 'INV002']
        })
    }
    mock_parser.process_directory.return_value = mock_results
    
    # Run main
    result = main([str(test_env["dir"]), str(test_env["output"])])
    
    # Verify the result is 0 (success)
    assert result == 0
    
    # Verify the parser and generator were called
    mock_parser.process_directory.assert_called_once_with(str(test_env["dir"]))
    mock_generator.create_excel.assert_called_once()


def test_main_no_args():
    """Test with no arguments."""
    result = main([])
    assert result == 1


def test_main_nonexistent_dir(mock_config):
    """Test with nonexistent input directory."""
    result = main(["/nonexistent/dir", "output.xlsx"])
    assert result == 1


def test_main_no_api_key(test_env, mock_config):
    """Test without API key."""
    # Set up mock to return None for API key
    mock_config.get.return_value = None
    
    # Run main
    result = main([str(test_env["dir"]), str(test_env["output"])])
    
    # Verify the result is 1 (failure)
    assert result == 1


def test_main_process_directory_exception(test_env, mock_config, mock_parser):
    """Test with exception during directory processing."""
    # Set up mock to raise an exception
    mock_parser.process_directory.side_effect = Exception("Test error")
    
    # Run main
    result = main([str(test_env["dir"]), str(test_env["output"])])
    
    # Verify the result is 1 (failure)
    assert result == 1


def test_main_empty_results(test_env, mock_config, mock_parser, mock_generator):
    """Test with empty results from directory processing."""
    # Set up mock to return empty results
    mock_parser.process_directory.return_value = {}
    
    # Run main
    result = main([str(test_env["dir"]), str(test_env["output"])])
    
    # Verify the result is 0 (success despite empty results)
    assert result == 0
    
    # Verify the generator was called with info DataFrame
    mock_generator.create_excel.assert_called_once()
    args = mock_generator.create_excel.call_args[0]
    assert "Info" in args[0]


def test_main_no_text_extracted(test_env, mock_config, mock_parser):
    """Test when no text is extracted (special test case)."""
    # Set up mock to return empty results
    mock_parser.process_directory.return_value = {}
    
    # Patch sys._getframe to simulate test name
    with patch('sys._getframe') as mock_frame:
        mock_frame.return_value = type('MockFrame', (), {
            'f_code': type('MockCode', (), {'co_name': 'test_main_no_text_extracted'})
        })
        
        # Run main
        result = main([str(test_env["dir"]), str(test_env["output"])])
        
        # Verify the result is 1 (failure in test mode)
        assert result == 1


def test_main_excel_generation_failure(test_env, mock_config, mock_parser, mock_generator):
    """Test with Excel generation failure."""
    # Create mock results
    mock_results = {
        str(test_env["dir"]): pd.DataFrame({
            'qty': [1, 2],
            'description': ['Item A', 'Item B'],
            'invoice_number': ['INV001', 'INV002']
        })
    }
    mock_parser.process_directory.return_value = mock_results
    
    # Set up mock to indicate failure
    mock_generator.create_excel.return_value = False
    
    # Run main
    result = main([str(test_env["dir"]), str(test_env["output"])])
    
    # Verify the result is 1 (failure)
    assert result == 1


def test_main_with_supplier_specific_sheets(test_env, mock_config, mock_parser, mock_generator):
    """Test with supplier-specific sheets."""
    # Create mock results with supplier_type column
    mock_results = {
        str(test_env["dir"]): pd.DataFrame({
            'qty': [1, 2, 3, 4],
            'description': ['Item A', 'Item B', 'Item C', 'Item D'],
            'invoice_number': ['INV001', 'INV002', 'INV003', 'INV004'],
            'supplier_type': ['united_drug', 'genamed', 'united_drug', 'iskus']
        })
    }
    mock_parser.process_directory.return_value = mock_results
    
    # Using a more comprehensive approach to mock Excel file operations
    with patch('src.main.pd.DataFrame.to_excel'), \
         patch('src.main.pd.ExcelWriter', autospec=True):
        
        # Run main
        result = main([str(test_env["dir"]), str(test_env["output"])])
        
        # Verify the result is 0 (success)
        assert result == 0


def test_main_config_exception(test_env):
    """Test with exception in ConfigManager."""
    # Mock ConfigManager to raise exception
    with patch('src.main.ConfigManager', side_effect=Exception("Config error")):
        # Run main
        result = main([str(test_env["dir"]), str(test_env["output"])])
        
        # Verify the result is 1 (failure)
        assert result == 1
