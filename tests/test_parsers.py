"""Test parsers module."""
from unittest.mock import Mock, patch
import pytest
import os
from src.parsers.image_parser import ImageParser

@pytest.fixture
def parser():
    """Create a parser instance."""
    return ImageParser(api_key="test_key")

def test_process_image_success(parser, tmp_path):
    """Test processing image file."""
    test_image = tmp_path / "test.jpg"
    test_image.write_bytes(b"test image")

    with patch('PIL.Image.open') as mock_open, \
         patch.object(parser.extractor, 'extract_text', return_value='Test content'):
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.save = lambda f, format: f.write(b"test image bytes")
        mock_open.return_value = mock_img

        result = parser.process_image(str(test_image))
        assert result == {"content": "Test content"}

def test_process_image_failure(parser, tmp_path):
    """Test processing image with failure."""
    test_image = tmp_path / "test.jpg"
    test_image.write_bytes(b"test image")

    with patch('PIL.Image.open') as mock_open, \
         patch.object(parser.extractor, 'extract_text', return_value=None):
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.save = lambda f, format: f.write(b"test image bytes")
        mock_open.return_value = mock_img

        result = parser.process_image(str(test_image))
        assert result is None

def test_process_pdf_success(parser, tmp_path):
    """Test processing PDF file."""
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(b"test pdf")

    with patch('fitz.open') as mock_fitz, \
         patch('PIL.Image.frombytes') as mock_frombytes, \
         patch('PIL.Image.Image.save') as mock_save, \
         patch('PIL.ImageEnhance.Contrast') as mock_contrast, \
         patch('fitz.Matrix') as mock_matrix, \
         patch('fitz.csRGB') as mock_csrgb, \
         patch.object(parser.extractor, 'extract_text', return_value='Test content'):
        # Mock Matrix and csRGB
        matrix_instance = Mock()
        mock_matrix.return_value = matrix_instance
        mock_csrgb.return_value = Mock()

        # Mock PDF document
        mock_doc = Mock()
        mock_doc.__len__ = lambda _: 1
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.width = 100
        mock_pixmap.height = 100
        mock_pixmap.samples = b"test image data"
        mock_page.get_pixmap = lambda matrix=None, colorspace=None: mock_pixmap
        mock_doc.load_page.return_value = mock_page
        mock_fitz.return_value = mock_doc

        # Mock PIL Image
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_frombytes.return_value = mock_img

        # Mock contrast
        mock_contrast_instance = Mock()
        mock_contrast_instance.enhance.return_value = mock_img
        mock_contrast.return_value = mock_contrast_instance

        # Mock save
        mock_save.side_effect = lambda f, format, quality=None: f.write(b"test image bytes")

        result = parser.process_pdf(str(test_pdf))
        assert result == [{"content": "Test content"}]

def test_process_pdf_failure(parser, tmp_path):
    """Test processing PDF with failure."""
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(b"test pdf")

    with patch('fitz.open') as mock_fitz, \
         patch.object(parser.extractor, 'extract_text', return_value=None):
        mock_doc = Mock()
        mock_doc.__len__ = lambda _: 1
        mock_page = Mock()
        mock_page.get_pixmap = lambda matrix=None, colorspace=None: None
        mock_doc.load_page.return_value = mock_page
        mock_fitz.return_value = mock_doc

        result = parser.process_pdf(str(test_pdf))
        assert result is None

def test_process_file_image(parser, tmp_path):
    """Test processing image file."""
    test_image = tmp_path / "test.jpg"
    test_image.write_bytes(b"test image")

    with patch('PIL.Image.open') as mock_open, \
         patch.object(parser.extractor, 'extract_text', return_value='Test content'):
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.save = lambda f, format: f.write(b"test image bytes")
        mock_open.return_value = mock_img

        result = parser.process_file(str(test_image))
        assert result == [{"content": "Test content"}]

def test_process_file_pdf(parser, tmp_path):
    """Test processing PDF file."""
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(b"test pdf")

    with patch('fitz.open') as mock_fitz, \
         patch('PIL.Image.frombytes') as mock_frombytes, \
         patch('PIL.Image.Image.save') as mock_save, \
         patch('PIL.ImageEnhance.Contrast') as mock_contrast, \
         patch('fitz.Matrix') as mock_matrix, \
         patch('fitz.csRGB') as mock_csrgb, \
         patch.object(parser.extractor, 'extract_text', return_value='Test content'):
        # Mock Matrix and csRGB
        matrix_instance = Mock()
        mock_matrix.return_value = matrix_instance
        mock_csrgb.return_value = Mock()

        # Mock PDF document
        mock_doc = Mock()
        mock_doc.__len__ = lambda _: 1
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.width = 100
        mock_pixmap.height = 100
        mock_pixmap.samples = b"test image data"
        mock_page.get_pixmap = lambda matrix=None, colorspace=None: mock_pixmap
        mock_doc.load_page.return_value = mock_page
        mock_fitz.return_value = mock_doc

        # Mock PIL Image
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_frombytes.return_value = mock_img

        # Mock contrast
        mock_contrast_instance = Mock()
        mock_contrast_instance.enhance.return_value = mock_img
        mock_contrast.return_value = mock_contrast_instance

        # Mock save
        mock_save.side_effect = lambda f, format, quality=None: f.write(b"test image bytes")

        result = parser.process_file(str(test_pdf))
        assert result == [{"content": "Test content"}]

def test_process_file_unsupported(parser, tmp_path):
    """Test processing unsupported file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    result = parser.process_file(str(test_file))
    assert result is None

def test_parse_directory_success(parser, tmp_path):
    """Test parsing directory."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Create test files
    test_image = test_dir / "test.jpg"
    test_image.write_bytes(b"test image")

    test_pdf = test_dir / "test.pdf"
    test_pdf.write_bytes(b"test pdf")

    with patch('PIL.Image.open') as mock_open, \
         patch('fitz.open') as mock_fitz, \
         patch('PIL.Image.frombytes') as mock_frombytes, \
         patch('PIL.Image.Image.save') as mock_save, \
         patch('PIL.ImageEnhance.Contrast') as mock_contrast, \
         patch('fitz.Matrix') as mock_matrix, \
         patch('fitz.csRGB') as mock_csrgb, \
         patch.object(parser.extractor, 'extract_text', return_value='Test content'):
        # Mock Matrix and csRGB
        matrix_instance = Mock()
        mock_matrix.return_value = matrix_instance
        mock_csrgb.return_value = Mock()

        # Mock image
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_open.return_value = mock_img

        # Mock PDF document
        mock_doc = Mock()
        mock_doc.__len__ = lambda _: 1
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.width = 100
        mock_pixmap.height = 100
        mock_pixmap.samples = b"test image data"
        mock_page.get_pixmap = lambda matrix=None, colorspace=None: mock_pixmap
        mock_doc.load_page.return_value = mock_page
        mock_fitz.return_value = mock_doc

        # Mock PIL Image for PDF
        mock_img_pdf = Mock()
        mock_img_pdf.mode = 'RGB'
        mock_frombytes.return_value = mock_img_pdf

        # Mock contrast
        mock_contrast_instance = Mock()
        mock_contrast_instance.enhance.return_value = mock_img_pdf
        mock_contrast.return_value = mock_contrast_instance

        # Mock save
        mock_save.side_effect = lambda f, format, quality=None: f.write(b"test image bytes")

        result = parser.parse_directory(str(test_dir))
        assert "test_dir" in result
        assert len(result["test_dir"]) == 2
        assert result["test_dir"][0]["content"] == "Test content"
        assert result["test_dir"][1]["content"] == "Test content"

def test_parse_directory_empty(parser, tmp_path):
    """Test parsing empty directory."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    result = parser.parse_directory(str(test_dir))
    assert isinstance(result, dict)
    assert len(result) == 0

def test_parse_directory_nonexistent(parser):
    """Test parsing nonexistent directory."""
    with pytest.raises(Exception, match="Directory not found: nonexistent_dir"):
        parser.parse_directory("nonexistent_dir")

def test_parse_directory_not_a_directory(parser, tmp_path):
    """Test parsing a file as directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    with pytest.raises(Exception, match=f"Not a directory: {test_file}"):
        parser.parse_directory(str(test_file))
