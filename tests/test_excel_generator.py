"""Test excel generator module."""
import os
import pytest
from unittest.mock import Mock, patch
import pandas as pd
from src.generators.excel_generator import ExcelGenerator

@pytest.fixture
def generator():
    return ExcelGenerator()

def test_init():
    """Test initialization."""
    generator = ExcelGenerator()
    assert isinstance(generator, ExcelGenerator)

def test_clean_sheet_name():
    """Test sheet name cleaning."""
    generator = ExcelGenerator()
    assert generator.clean_sheet_name("test") == "test"
    assert generator.clean_sheet_name("test[]") == "test"
    assert generator.clean_sheet_name("a" * 32) == "a" * 31
    assert generator.clean_sheet_name("") == "Sheet1"
    assert generator.clean_sheet_name(None) == "Sheet1"
    assert generator.clean_sheet_name("test:*?/\\") == "test"

def test_create_excel_success(tmp_path, generator):
    """Test successful Excel creation."""
    output_path = tmp_path / "test.xlsx"
    data = {
        "sheet1": [{"content": "test1"}],
        "sheet2": [{"content": "test2"}]
    }
    
    assert generator.create_excel(data, str(output_path)) is True
    assert os.path.exists(output_path)

def test_create_excel_empty_data(tmp_path, generator):
    """Test Excel creation with empty data."""
    output_path = tmp_path / "test.xlsx"
    assert generator.create_excel({}, str(output_path)) is False

def test_create_excel_invalid_path(generator):
    """Test Excel creation with invalid path."""
    data = {"sheet1": [{"content": "test"}]}
    assert generator.create_excel(data, "/invalid/path/test.xlsx") is False

def test_create_excel_write_error(tmp_path, generator):
    """Test Excel creation with write error."""
    output_path = tmp_path / "test.xlsx"
    data = {"sheet1": [{"content": "test"}]}
    
    with patch('pandas.DataFrame.to_excel', side_effect=Exception("Write error")):
        assert generator.create_excel(data, str(output_path)) is False

def test_create_excel_duplicate_sheets(tmp_path, generator):
    """Test Excel creation with duplicate sheet names."""
    output_path = tmp_path / "test.xlsx"
    data = {
        "test": [{"content": "test1"}],
        "test[]": [{"content": "test2"}]
    }
    
    assert generator.create_excel(data, str(output_path)) is True
    assert os.path.exists(output_path)

def test_create_excel_long_sheet_names(tmp_path, generator):
    """Test Excel creation with long sheet names."""
    output_path = tmp_path / "test.xlsx"
    data = {
        "a" * 50: [{"content": "test1"}],
        "b" * 50: [{"content": "test2"}]
    }
    
    assert generator.create_excel(data, str(output_path)) is True
    assert os.path.exists(output_path)

def test_create_excel_special_chars(tmp_path, generator):
    """Test Excel creation with special characters in sheet names."""
    output_path = tmp_path / "test.xlsx"
    data = {
        "test:*?/\\[]": [{"content": "test1"}],
        "test@#$%^&": [{"content": "test2"}]
    }
    
    assert generator.create_excel(data, str(output_path)) is True
    assert os.path.exists(output_path)

def test_create_excel_empty_sheets(tmp_path, generator):
    """Test Excel creation with empty sheets."""
    output_path = tmp_path / "test.xlsx"
    data = {
        "sheet1": [],
        "sheet2": []
    }
    
    assert generator.create_excel(data, str(output_path)) is False

def test_create_excel_invalid_content(tmp_path, generator):
    """Test Excel creation with invalid content."""
    output_path = tmp_path / "test.xlsx"
    data = {
        "sheet1": [{"invalid": "test"}],
        "sheet2": [{"content": None}]
    }
    
    assert generator.create_excel(data, str(output_path)) is False

def test_create_excel_mixed_content(tmp_path, generator):
    """Test Excel creation with mixed valid and invalid content."""
    output_path = tmp_path / "test.xlsx"
    data = {
        "sheet1": [{"content": "test1"}, {"invalid": "test"}],
        "sheet2": [{"content": "test2"}, {"content": None}]
    }
    
    assert generator.create_excel(data, str(output_path)) is True
    assert os.path.exists(output_path)

def test_create_excel_verify_content(tmp_path, generator):
    """Test Excel creation and verify content."""
    output_path = tmp_path / "test.xlsx"
    data = {
        "sheet1": [{"content": "test1"}],
        "sheet2": [{"content": "test2"}]
    }
    
    assert generator.create_excel(data, str(output_path)) is True
    
    # Verify content
    excel_file = pd.ExcelFile(output_path)
    assert "sheet1" in excel_file.sheet_names
    assert "sheet2" in excel_file.sheet_names
    
    df1 = pd.read_excel(output_path, sheet_name="sheet1")
    df2 = pd.read_excel(output_path, sheet_name="sheet2")
    
    assert df1.iloc[0]["Content"] == "test1"
    assert df2.iloc[0]["Content"] == "test2"
