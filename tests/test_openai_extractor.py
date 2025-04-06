"""Test OpenAI extractor module."""
from unittest.mock import Mock, patch
import pytest
import os
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
    extractor = OpenAIExtractor(api_key="test_key")
    assert extractor.api_key == "test_key"

def test_init_without_api_key():
    """Test initialization without API key."""
    with patch('os.getenv', return_value=None):
        with pytest.raises(Exception, match="OpenAI API key not provided"):
            OpenAIExtractor()

def test_extract_text_success():
    """Test text extraction success."""
    with patch('openai.OpenAI') as mock_openai, \
         patch('src.utils.config_manager.ConfigManager.get') as mock_get:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test content"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_get.side_effect = lambda *args: "gpt-4-vision-preview" if args[1] == "vision" and args[2] == "model" else 1000
        
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_text(b"test image")
        assert result == "Test content"

def test_extract_text_empty_input():
    """Test text extraction with empty input."""
    extractor = OpenAIExtractor(api_key="test_key")
    result = extractor.extract_text(None)
    assert result is None

def test_extract_text_api_error():
    """Test text extraction with API error."""
    with patch('openai.OpenAI') as mock_openai, \
         patch('src.utils.config_manager.ConfigManager.get') as mock_get:
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        mock_get.side_effect = lambda *args: "gpt-4-vision-preview" if args[1] == "vision" and args[2] == "model" else 1000
        
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_text(b"test image")
        assert result is None

def test_extract_structured_data_success():
    """Test structured data extraction success."""
    with patch('openai.OpenAI') as mock_openai, \
         patch('src.utils.config_manager.ConfigManager.get') as mock_get:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """{
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
        }"""
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_get.side_effect = lambda *args: "gpt-4" if args[1] == "chat" and args[2] == "model" else 2000
        
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_structured_data("Test invoice text")
        assert result["invoice_number"] == "INV-001"
        assert result["invoice_date"] == "2025-04-01"
        assert result["vendor"] == "Test Vendor"
        assert result["customer"] == "Test Customer"
        assert result["total_amount"] == 100.0
        assert result["currency"] == "USD"
        assert result["payment_terms"] == "Net 30"
        assert len(result["items"]) == 1
        assert result["items"][0]["description"] == "Test Item"
        assert result["items"][0]["quantity"] == 1
        assert result["items"][0]["unit_price"] == 100.0
        assert result["items"][0]["amount"] == 100.0

def test_extract_structured_data_code_blocks():
    """Test structured data extraction with code blocks."""
    with patch('openai.OpenAI') as mock_openai, \
         patch('src.utils.config_manager.ConfigManager.get') as mock_get:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """```json
{
    "invoice_number": "INV-001",
    "invoice_date": "2025-04-01",
    "vendor": "Test Vendor",
    "customer": "Test Customer",
    "total_amount": 100.0,
    "currency": "USD",
    "payment_terms": "Net 30",
    "items": []
}
```"""
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_get.side_effect = lambda *args: "gpt-4" if args[1] == "chat" and args[2] == "model" else 2000
        
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_structured_data("Test invoice text")
        assert result["invoice_number"] == "INV-001"
        assert result["invoice_date"] == "2025-04-01"
        assert result["vendor"] == "Test Vendor"
        assert result["items"] == []

def test_extract_structured_data_empty_input():
    """Test structured data extraction with empty input."""
    extractor = OpenAIExtractor(api_key="test_key")
    result = extractor.extract_structured_data(None)
    assert result is None

def test_extract_structured_data_api_error():
    """Test structured data extraction with API error."""
    with patch('openai.OpenAI') as mock_openai, \
         patch('src.utils.config_manager.ConfigManager.get') as mock_get:
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        mock_get.side_effect = lambda *args: "gpt-4" if args[1] == "chat" and args[2] == "model" else 2000
        
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_structured_data("Test invoice text")
        assert result["raw_text"] == "Test invoice text"

def test_extract_structured_data_json_error():
    """Test structured data extraction with JSON parsing error."""
    with patch('openai.OpenAI') as mock_openai, \
         patch('src.utils.config_manager.ConfigManager.get') as mock_get:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON {"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_get.side_effect = lambda *args: "gpt-4" if args[1] == "chat" and args[2] == "model" else 2000
        
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_structured_data("Test invoice text")
        assert result["raw_text"] == "Test invoice text"

def test_extract_data_success():
    """Test data extraction success."""
    with patch.object(OpenAIExtractor, 'extract_text', return_value="Test invoice text"), \
         patch.object(OpenAIExtractor, 'extract_structured_data') as mock_extract_structured:
        mock_extract_structured.return_value = {
            "invoice_number": "INV-001",
            "invoice_date": "2025-04-01",
            "vendor": "Test Vendor",
            "items": []
        }
        
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_data(b"test image")
        assert result["invoice_number"] == "INV-001"
        assert result["invoice_date"] == "2025-04-01"
        assert result["vendor"] == "Test Vendor"
        assert result["items"] == []

def test_extract_data_text_extraction_failed():
    """Test data extraction with text extraction failure."""
    with patch.object(OpenAIExtractor, 'extract_text', return_value=None):
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_data(b"test image")
        assert result is None

def test_extract_data_structured_extraction_failed():
    """Test data extraction with structured extraction failure."""
    with patch.object(OpenAIExtractor, 'extract_text', return_value="Test invoice text"), \
         patch.object(OpenAIExtractor, 'extract_structured_data', return_value=None):
        extractor = OpenAIExtractor(api_key="test_key")
        result = extractor.extract_data(b"test image")
        assert result["raw_text"] == "Test invoice text"
