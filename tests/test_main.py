import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from src.main import main, load_config
from loguru import logger

# Disable logger during tests
logger.remove()

@pytest.fixture
def test_config():
    return {
        'openai': {
            'api_key': 'OPEN_API_KEY',
            'vision': {
                'model': 'gpt-4-vision-preview',
                'max_tokens': 1000,
                'messages': [{
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': 'Test message'},
                        {'type': 'image_url', 'image_url': {'url_prefix': 'data:image/jpeg;base64,'}}
                    ]
                }]
            }
        },
        'output': {
            'excel': {
                'default_filename': 'output.xlsx'
            }
        }
    }

def test_load_config(test_config):
    with patch('yaml.safe_load', return_value=test_config), \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', return_value="/test/conf/api_config.yaml"), \
         patch('builtins.open', MagicMock()):
        config = load_config()
        assert config == test_config

def test_load_config_error():
    with patch('yaml.safe_load', side_effect=Exception("Test error")), \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', return_value="/test/conf/api_config.yaml"), \
         patch('builtins.open', MagicMock()), \
         pytest.raises(Exception, match="Failed to load configuration: Test error"):
        load_config()

def test_main_success(tmp_path, test_config):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "test.jpg").write_bytes(b"test image")

    with patch('sys.argv', ['script.py', str(input_dir)]), \
         patch('yaml.safe_load', return_value=test_config), \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', return_value="/test/conf/api_config.yaml"), \
         patch('builtins.open', MagicMock()), \
         patch('src.parsers.image_parser.ImageParser.parse_directory') as mock_parse, \
         patch('src.generators.excel_generator.ExcelGenerator.create_excel') as mock_create, \
         patch('src.generators.excel_generator.ExcelGenerator.save_excel', return_value=True) as mock_save, \
         patch('loguru.logger.error') as mock_logger:
        
        mock_parse.return_value = {"dir1": [{"content": "test"}]}
        main()
        
        mock_parse.assert_called_once()
        mock_create.assert_called_once()
        mock_save.assert_called_once()
        mock_logger.assert_not_called()

def test_main_file_not_found():
    with patch('sys.argv', ['script.py', '/nonexistent']), \
         patch('yaml.safe_load', return_value={'openai': {'api_key': 'OPEN_API_KEY'}}), \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', return_value="/test/conf/api_config.yaml"), \
         patch('builtins.open', MagicMock()), \
         patch('os.path.exists', return_value=False), \
         patch('loguru.logger.error') as mock_logger, \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    mock_logger.assert_called_once_with("Error: Directory '/nonexistent' not found")

def test_main_no_data_extracted(tmp_path, test_config):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch('sys.argv', ['script.py', str(input_dir)]), \
         patch('yaml.safe_load', return_value=test_config), \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', return_value="/test/conf/api_config.yaml"), \
         patch('builtins.open', MagicMock()), \
         patch('src.parsers.image_parser.ImageParser.parse_directory', return_value={"dir1": []}), \
         patch('loguru.logger.error') as mock_logger, \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    mock_logger.assert_called_once_with("No data was extracted from the images")

def test_main_save_excel_error(tmp_path, test_config):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch('sys.argv', ['script.py', str(input_dir)]), \
         patch('yaml.safe_load', return_value=test_config), \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', return_value="/test/conf/api_config.yaml"), \
         patch('builtins.open', MagicMock()), \
         patch('src.parsers.image_parser.ImageParser.parse_directory') as mock_parse, \
         patch('src.generators.excel_generator.ExcelGenerator.create_excel'), \
         patch('src.generators.excel_generator.ExcelGenerator.save_excel', return_value=False), \
         patch('loguru.logger.error') as mock_logger, \
         pytest.raises(SystemExit) as exc_info:
        
        mock_parse.return_value = {"dir1": [{"content": "test"}]}
        main()
    assert exc_info.value.code == 1
    mock_logger.assert_called_once_with("Error: Failed to save Excel file")

def test_main_entry_point():
    with patch('sys.argv', ['script.py']), \
         patch('yaml.safe_load', return_value={'openai': {'api_key': 'OPEN_API_KEY'}}), \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', return_value="/test/conf/api_config.yaml"), \
         patch('builtins.open', MagicMock()), \
         patch('loguru.logger.error') as mock_logger, \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    mock_logger.assert_called_once_with("Usage: python main.py <input_directory>")

def test_main_general_error(tmp_path, test_config):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch('sys.argv', ['script.py', str(input_dir)]), \
         patch('yaml.safe_load', return_value=test_config), \
         patch('os.path.dirname', return_value="/test"), \
         patch('os.path.join', return_value="/test/conf/api_config.yaml"), \
         patch('builtins.open', MagicMock()), \
         patch('src.parsers.image_parser.ImageParser.parse_directory', side_effect=Exception("Test error")), \
         patch('loguru.logger.error') as mock_logger, \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    mock_logger.assert_called_once_with("Error: Test error")
