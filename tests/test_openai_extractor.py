"""Test OpenAI extractor module."""
import pytest
from unittest.mock import Mock, patch
from src.parsers.openai_extractor import OpenAIExtractor

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
def extractor(mock_openai):
    return OpenAIExtractor("test_api_key")

def test_init_with_api_key():
    """Test initialization with API key."""
    extractor = OpenAIExtractor("test_api_key")
    assert extractor.api_key == "test_api_key"

def test_init_without_api_key():
    """Test initialization without API key."""
    with pytest.raises(Exception):
        OpenAIExtractor()

def test_extract_text_success(extractor):
    """Test successful text extraction."""
    result = extractor.extract_text(b"test image")
    assert result == "Test content"

def test_extract_text_empty_input(extractor):
    """Test text extraction with empty input."""
    result = extractor.extract_text(b"")
    assert result is None

def test_extract_text_api_error(extractor):
    """Test text extraction with API error."""
    with patch('openai.OpenAI') as mock:
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock.return_value = mock_client
        
        extractor = OpenAIExtractor("test_api_key")
        result = extractor.extract_text(b"test image")
        assert result is None
