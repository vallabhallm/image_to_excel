import pytest
import pandas as pd
from src.generators.excel_generator import ExcelGenerator
from unittest.mock import patch, Mock

@pytest.fixture
def excel_generator():
    return ExcelGenerator()

def test_create_excel_with_dict(excel_generator):
    # Test data organized by directory
    data = {
        "dir1": [{"col1": "value1", "col2": "value2"}],
        "dir2": [{"col1": "value3", "col2": "value4"}]
    }
    excel_generator.create_excel(data)
    assert "dir1" in excel_generator.data
    assert "dir2" in excel_generator.data
    assert isinstance(excel_generator.data["dir1"], pd.DataFrame)
    assert isinstance(excel_generator.data["dir2"], pd.DataFrame)

def test_create_excel_with_list(excel_generator):
    # Test data with multiple rows per directory
    data = {
        "dir1": [
            {"col1": "value1", "col2": "value2"},
            {"col1": "value3", "col2": "value4"}
        ]
    }
    excel_generator.create_excel(data)
    assert "dir1" in excel_generator.data
    assert len(excel_generator.data["dir1"]) == 2

def test_create_excel_with_simple_data(excel_generator):
    # Test data with simple structure
    data = {
        "root": [{"data": "test"}]
    }
    excel_generator.create_excel(data)
    assert "root" in excel_generator.data
    assert len(excel_generator.data["root"]) == 1

def test_save_excel_success(excel_generator, tmp_path):
    # Test successful save
    data = {
        "Sheet1": [{"col1": "value1"}]
    }
    excel_generator.create_excel(data)
    output_file = tmp_path / "test.xlsx"
    assert excel_generator.save_excel(str(output_file)) is True

def test_save_excel_no_data(excel_generator, tmp_path):
    # Test save with no data
    output_file = tmp_path / "test.xlsx"
    assert excel_generator.save_excel(str(output_file)) is False

def test_clean_sheet_name(excel_generator):
    """Test cleaning of sheet names"""
    # Test invalid characters
    assert excel_generator.clean_sheet_name('[Test]*Sheet?') == 'Test_Sheet'
    # Test length limit
    long_name = 'x' * 40
    assert len(excel_generator.clean_sheet_name(long_name)) <= 31

def test_clean_sheet_name_repeated_underscores(excel_generator):
    """Test handling of repeated underscores"""
    assert excel_generator.clean_sheet_name('Test__Sheet___Name') == 'Test_Sheet_Name'

def test_clean_sheet_name_empty(excel_generator):
    """Test handling of empty sheet name"""
    assert excel_generator.clean_sheet_name('') == 'Sheet1'
    assert excel_generator.clean_sheet_name(None) == 'Sheet1'

def test_save_excel_error(excel_generator, tmp_path, monkeypatch):
    def mock_excel_writer(*args, **kwargs):
        raise Exception("Test error")
    
    monkeypatch.setattr(pd, "ExcelWriter", mock_excel_writer)
    
    data = {
        "Sheet1": [{"col1": "value1"}]
    }
    excel_generator.create_excel(data)
    output_file = tmp_path / "test.xlsx"
    assert excel_generator.save_excel(str(output_file)) is False
