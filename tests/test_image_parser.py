import os
import sys
import pytest
from unittest.mock import patch, mock_open, MagicMock
from io import BytesIO
from src.parsers.image_parser import ImageParser

@pytest.fixture
def parser():
    config = {
        'openai': {
            'api_key': 'test-key',
            'vision': {
                'model': 'test-model',
                'max_tokens': 1000
            }
        }
    }
    return ImageParser(config)

def test_is_image_file(parser):
    assert parser.is_image_file("test.jpg") is True
    assert parser.is_image_file("test.jpeg") is True
    assert parser.is_image_file("test.png") is True
    assert parser.is_image_file("test.pdf") is True
    assert parser.is_image_file("test.txt") is False

def test_process_file_unsupported_type(parser):
    """Test handling of unsupported file types"""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        result = parser.process_file("test.txt")
        assert result is None

def test_process_file_not_found(parser):
    """Test handling of non-existent files"""
    result = parser.process_file("nonexistent.jpg")
    assert result is None

def test_process_file_image_error(parser):
    """Test handling of image processing errors"""
    with patch("os.path.exists") as mock_exists, \
         patch.object(parser, "process_image", side_effect=Exception("Test error")):
        mock_exists.return_value = True
        result = parser.process_file("test.jpg")
        assert result is None

def test_process_image_with_bytes(parser):
    """Test processing an image from bytes"""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test content"
    
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        image_bytes = BytesIO(b"test image data")
        result = parser.process_image(image_bytes)
        assert result == {"content": "Test content"}

def test_process_image_with_file(parser):
    """Test processing an image from file"""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test content"
    
    with patch("builtins.open", mock_open(read_data=b"test image data")), \
         patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = parser.process_image("test.jpg")
        assert result == {"content": "Test content"}

def test_process_image_file_error(parser):
    """Test handling of file read errors in process_image"""
    with patch("builtins.open", side_effect=Exception("File read error")):
        result = parser.process_image("test.jpg")
        assert result is None

def test_process_file_success(parser):
    """Test successful processing of an image file"""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test content"
    
    with patch("os.path.exists") as mock_exists, \
         patch("builtins.open", mock_open(read_data=b"test")), \
         patch("openai.OpenAI") as mock_openai:
        mock_exists.return_value = True
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = parser.process_file("test.jpg")
        assert result == [{"content": "Test content"}]

def test_process_file_pdf(parser):
    """Test processing a PDF file"""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test content"
    
    with patch("os.path.exists") as mock_exists, \
         patch("fitz.open") as mock_fitz_open, \
         patch("openai.OpenAI") as mock_openai:
        mock_exists.return_value = True
        
        # Mock PDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_pixmap = MagicMock()
        mock_pixmap.tobytes.return_value = b"test image data"  # Return actual bytes
        mock_page.get_pixmap.return_value = mock_pixmap
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = parser.process_file("test.pdf")
        assert result == [{"content": "Test content"}]

def test_parse_directory_success(parser):
    """Test successful directory parsing"""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test content"
    
    with patch("os.path.exists") as mock_exists, \
         patch("os.walk") as mock_walk, \
         patch("os.path.isfile") as mock_isfile, \
         patch("builtins.open", mock_open(read_data=b"test")), \
         patch("openai.OpenAI") as mock_openai:
        mock_exists.return_value = True
        mock_walk.return_value = [("test_dir", [], ["test.jpg"])]
        mock_isfile.return_value = True
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = parser.parse_directory("test_dir")
        assert "test_dir" in result
        assert len(result["test_dir"]) == 1
        assert result["test_dir"][0] == [{"content": "Test content"}]

def test_parse_directory_no_images(parser):
    """Test directory parsing with no valid images"""
    with patch("os.path.exists") as mock_exists, \
         patch("os.walk") as mock_walk:
        mock_exists.return_value = True
        mock_walk.return_value = [("test_dir", [], ["test.txt"])]
        
        result = parser.parse_directory("test_dir")
        assert "test_dir" in result
        assert len(result["test_dir"]) == 0

def test_parse_directory_error(parser):
    """Test directory parsing with non-existent directory"""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        with pytest.raises(Exception):
            parser.parse_directory("test_dir")

def test_parse_directory_process_error(parser):
    """Test directory parsing with processing error"""
    with patch("os.path.exists") as mock_exists, \
         patch("os.walk") as mock_walk, \
         patch("os.path.isfile") as mock_isfile, \
         patch.object(parser, "process_file", return_value=None):
        mock_exists.return_value = True
        mock_walk.return_value = [("test_dir", [], ["test.jpg"])]
        mock_isfile.return_value = True
        
        result = parser.parse_directory("test_dir")
        assert "test_dir" in result
        assert len(result["test_dir"]) == 0

def test_init_with_config_error(parser):
    """Test initialization with config loading error"""
    with patch('builtins.open', side_effect=Exception("Config file not found")):
        with pytest.raises(Exception) as exc_info:
            ImageParser("test-key")
        assert "Failed to load configuration file" in str(exc_info.value)

def test_process_image_invalid_path_type():
    """Test process_image with invalid path type"""
    parser = ImageParser({'openai': {'api_key': 'test-key'}})
    result = parser.process_image(123)  # Invalid type
    assert result is None

def test_process_image_api_error(parser):
    """Test process_image with API error"""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        result = parser.process_image("test.jpg")
        assert result is None

def test_process_image_invalid_response(parser):
    """Test process_image with invalid API response"""
    mock_response = MagicMock()
    mock_response.choices = []  # Empty choices
    
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = parser.process_image("test.jpg")
        assert result is None

def test_process_file_pdf_error(parser):
    """Test PDF processing error"""
    with patch("os.path.exists") as mock_exists, \
         patch("fitz.open") as mock_fitz_open:
        mock_exists.return_value = True
        mock_fitz_open.side_effect = Exception("PDF Error")
        
        result = parser.process_file("test.pdf")
        assert result is None

def test_process_file_pdf_page_error(parser):
    """Test PDF page processing error"""
    with patch("os.path.exists") as mock_exists, \
         patch("fitz.open") as mock_fitz_open:
        mock_exists.return_value = True
        
        # Mock PDF document with page error
        mock_doc = MagicMock()
        mock_doc.load_page.side_effect = Exception("Page Error")
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc
        
        result = parser.process_file("test.pdf")
        assert result is None

def test_process_file_pdf_no_pages(parser):
    """Test PDF with no pages"""
    with patch("os.path.exists") as mock_exists, \
         patch("fitz.open") as mock_fitz_open:
        mock_exists.return_value = True
        
        # Mock empty PDF document
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 0
        mock_fitz_open.return_value = mock_doc
        
        result = parser.process_file("test.pdf")
        assert result == []

def test_process_file_pdf_some_pages_fail(parser):
    """Test PDF where some pages fail to process"""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test content"
    
    with patch("os.path.exists") as mock_exists, \
         patch("fitz.open") as mock_fitz_open, \
         patch("openai.OpenAI") as mock_openai:
        mock_exists.return_value = True
        
        # Mock PDF document with two pages, one fails
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page2 = MagicMock()
        mock_pixmap1 = MagicMock()
        mock_pixmap2 = MagicMock()
        
        mock_pixmap1.tobytes.return_value = b"test image data 1"
        mock_pixmap2.tobytes.side_effect = Exception("Pixmap Error")
        
        mock_page1.get_pixmap.return_value = mock_pixmap1
        mock_page2.get_pixmap.return_value = mock_pixmap2
        
        mock_doc.load_page.side_effect = [mock_page1, mock_page2]
        mock_doc.__len__.return_value = 2
        mock_fitz_open.return_value = mock_doc
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = parser.process_file("test.pdf")
        assert len(result) == 1
        assert result[0] == {"content": "Test content"}

def test_process_image_api_error_with_bytes(parser):
    """Test process_image with API error using bytes input"""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        image_bytes = BytesIO(b"test image data")
        result = parser.process_image(image_bytes)
        assert result is None

def test_process_image_api_error_with_invalid_response(parser):
    """Test process_image with invalid API response format"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]  # Missing message attribute
    
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = parser.process_image("test.jpg")
        assert result is None

def test_process_image_api_error_with_none_response(parser):
    """Test process_image with None API response"""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = None
        mock_openai.return_value = mock_client
        
        result = parser.process_image("test.jpg")
        assert result is None

def test_process_image_api_error_with_empty_content(parser):
    """Test process_image with empty content in API response"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=""))]
    
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = parser.process_image("test.jpg")
        assert result is None

def test_load_config_yaml_error():
    """Test config loading with YAML parsing error"""
    with patch('builtins.open', mock_open(read_data="invalid: yaml: content")), \
         patch('yaml.safe_load', side_effect=Exception("YAML parsing error")):
        with pytest.raises(Exception) as exc_info:
            ImageParser("test-key")
        assert "Failed to load configuration file" in str(exc_info.value)