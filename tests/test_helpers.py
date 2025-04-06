import pytest
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
from PIL import Image
import io
from src.utils.helpers import (
    is_valid_file_type, 
    get_file_type, 
    load_image, 
    convert_to_rgb,
    save_image,
    format_data
)

def test_is_valid_file_type():
    """Test file type validation."""
    assert is_valid_file_type("test.jpg") is True
    assert is_valid_file_type("test.jpeg") is True
    assert is_valid_file_type("test.png") is True
    assert is_valid_file_type("test.pdf") is True
    assert is_valid_file_type("test.txt") is False
    assert is_valid_file_type("test") is False
    assert is_valid_file_type("") is False

def test_get_file_type():
    """Test file type detection."""
    assert get_file_type("test.jpg") == "image"
    assert get_file_type("test.jpeg") == "image"
    assert get_file_type("test.png") == "image"
    assert get_file_type("test.pdf") == "pdf"
    assert get_file_type("test.txt") == "unknown"
    assert get_file_type("test") == "unknown"
    assert get_file_type("") == "unknown"

def create_test_image(mode='RGB'):
    """Create a test image for testing."""
    img = Image.new(mode, (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.read()

def test_load_image_success():
    """Test successful image loading."""
    test_image = create_test_image()
    
    with patch('builtins.open', mock_open(read_data=test_image)):
        image = load_image("test.png")
        assert isinstance(image, Image.Image)
        assert image.mode == 'RGB'
        assert image.size == (100, 100)

def test_load_image_failure():
    """Test image loading failure."""
    with patch('builtins.open', mock_open(read_data=b"invalid image data")):
        image = load_image("test.png")
        assert image is None

def test_convert_to_rgb_already_rgb():
    """Test RGB image conversion when already RGB."""
    img = Image.new('RGB', (100, 100), color='red')
    result = convert_to_rgb(img)
    assert result.mode == 'RGB'
    assert result is img  # Should return same object if already RGB

def test_convert_to_rgb_from_rgba():
    """Test RGBA to RGB conversion."""
    img = Image.new('RGBA', (100, 100), color='red')
    result = convert_to_rgb(img)
    assert result.mode == 'RGB'
    assert result is not img  # Should return new object

def test_convert_to_rgb_from_l():
    """Test L (grayscale) to RGB conversion."""
    img = Image.new('L', (100, 100), color=128)
    result = convert_to_rgb(img)
    assert result.mode == 'RGB'
    assert result is not img  # Should return new object

def test_save_image_success(tmp_path):
    """Test successful image saving."""
    img = Image.new('RGB', (100, 100), color='red')
    output_path = tmp_path / "test_output.png"
    
    assert save_image(img, str(output_path)) is True
    assert output_path.exists()
    
    # Verify the saved image
    saved_img = Image.open(output_path)
    assert saved_img.mode == 'RGB'
    assert saved_img.size == (100, 100)

def test_save_image_failure():
    """Test image saving failure."""
    img = Image.new('RGB', (100, 100), color='red')
    with patch('PIL.Image.Image.save') as mock_save:
        mock_save.side_effect = Exception("Failed to save image")
        assert save_image(img, "test.png") is False

def test_format_data():
    """Test data formatting."""
    input_data = [
        {"content": "test1"},
        {"content": "test2"},
        None,
        {"content": "test3"},
        {"invalid": "test4"},
        {}
    ]
    expected = ["test1", "test2", "test3"]
    assert format_data(input_data) == expected
    
    # Test with empty input
    assert format_data([]) == []
    
    # Test with None input
    assert format_data(None) == []
    
    # Test with invalid input
    assert format_data([None, {}, {"invalid": "test"}]) == []
