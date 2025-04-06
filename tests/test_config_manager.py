import pytest
from pathlib import Path
import yaml
from unittest.mock import patch, mock_open, Mock
from src.utils.config_manager import ConfigManager

@pytest.fixture(autouse=True)
def reset_config_manager():
    """Reset ConfigManager singleton between tests."""
    ConfigManager._instance = None
    ConfigManager._config = None
    yield

@pytest.fixture
def sample_config():
    return {
        'openai': {
            'api_key': 'test_key',
            'vision': {
                'model': 'gpt-4-vision-preview',
                'max_tokens': 1000
            }
        },
        'output': {
            'excel': {
                'default_filename': 'output.xlsx'
            }
        }
    }

def test_singleton_pattern():
    """Test that ConfigManager follows singleton pattern."""
    config1 = ConfigManager()
    config2 = ConfigManager()
    assert config1 is config2

def test_load_config_success(sample_config):
    """Test successful config loading."""
    mock_yaml = yaml.dump(sample_config)
    with patch('pathlib.Path.open', mock_open(read_data=mock_yaml)):
        config = ConfigManager()
        assert config.config == sample_config

def test_load_config_failure():
    """Test config loading failure."""
    with patch('pathlib.Path.open', side_effect=Exception("Failed to open file")):
        with pytest.raises(Exception) as exc_info:
            ConfigManager()
        assert "Failed to load configuration file" in str(exc_info.value)

def test_get_config_value(sample_config):
    """Test getting config values."""
    with patch('pathlib.Path.open', mock_open(read_data=yaml.dump(sample_config))):
        config = ConfigManager()
        assert config.get('openai', 'api_key') == 'test_key'
        assert config.get('openai', 'vision', 'model') == 'gpt-4-vision-preview'
        assert config.get('nonexistent') is None
        assert config.get('openai', 'nonexistent') is None
