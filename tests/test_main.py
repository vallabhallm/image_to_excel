"""Test main module."""
import os
import pytest
from unittest.mock import Mock, patch
from src.main import main
from src.utils.config_manager import ConfigManager

@pytest.fixture
def mock_openai():
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
    with patch('src.utils.config_manager.ConfigManager') as mock:
        mock_instance = Mock()
        mock_instance.get.return_value = "test_api_key"
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def test_env(tmp_path):
    """Create test environment."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    test_image = test_dir / "test.png"
    test_image.write_bytes(b"test image")
    output_file = tmp_path / "output.xlsx"
    return {"dir": test_dir, "image": test_image, "output": output_file}

def test_main_success(test_env, mock_openai, mock_config):
    """Test successful execution."""
    with patch('PIL.Image.open') as mock_open, \
         patch('src.generators.excel_generator.ExcelGenerator.create_excel', return_value=True):
        # Mock image processing
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.save = lambda f, format: f.write(b"test image bytes")
        mock_open.return_value = mock_img
        
        # Run main
        result = main([str(test_env["dir"]), str(test_env["output"])])
        assert result == 0

def test_main_no_args():
    """Test with no arguments."""
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 1

def test_main_input_not_found():
    """Test with nonexistent input directory."""
    with pytest.raises(SystemExit) as exc_info:
        main(["/nonexistent/dir", "output.xlsx"])
    assert exc_info.value.code == 1

def test_main_no_api_key(test_env, mock_config):
    """Test without API key."""
    mock_config.return_value.get.return_value = None
    with pytest.raises(SystemExit) as exc_info:
        main([str(test_env["dir"]), "output.xlsx"])
    assert exc_info.value.code == 1

def test_main_no_text_extracted(test_env, mock_openai, mock_config):
    """Test when no text is extracted from files."""
    with patch('PIL.Image.open') as mock_open, \
         patch('src.parsers.image_parser.ImageParser.parse_directory', return_value={}):
        # Mock image processing
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.save = lambda f, format: f.write(b"test image bytes")
        mock_open.return_value = mock_img
        
        with pytest.raises(SystemExit) as exc_info:
            main([str(test_env["dir"]), str(test_env["output"])])
        assert exc_info.value.code == 1

def test_main_excel_creation_failed(test_env, mock_openai, mock_config):
    """Test when Excel creation fails."""
    with patch('PIL.Image.open') as mock_open, \
         patch('src.generators.excel_generator.ExcelGenerator.create_excel', return_value=False):
        # Mock image processing
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.save = lambda f, format: f.write(b"test image bytes")
        mock_open.return_value = mock_img
        
        with pytest.raises(SystemExit) as exc_info:
            main([str(test_env["dir"]), str(test_env["output"])])
        assert exc_info.value.code == 1

def test_main_general_exception(test_env, mock_config):
    """Test general exception handling."""
    with patch('PIL.Image.open', side_effect=Exception("Test error")):
        with pytest.raises(SystemExit) as exc_info:
            main([str(test_env["dir"]), str(test_env["output"])])
        assert exc_info.value.code == 1

def test_config_load_error(test_env):
    """Test configuration loading error."""
    with patch('src.utils.config_manager.ConfigManager', side_effect=Exception("Config error")), \
         pytest.raises(SystemExit) as exc_info:
        main([str(test_env["dir"]), str(test_env["output"])])
    assert exc_info.value.code == 1
