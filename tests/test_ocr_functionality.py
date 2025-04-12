"""Test OCR functionality in the invoice parser."""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    """Create a GPT invoice parser instance with mocked OCR dependencies."""
    with patch('openai.OpenAI'):
        with patch('src.parsers.gpt_invoice_parser.PYPDF2_AVAILABLE', True):
            with patch('src.parsers.gpt_invoice_parser.EASYOCR_AVAILABLE', True):
                return GPTInvoiceParser(api_key="test_key")

def test_ocr_fallback_when_standard_extraction_fails(parser, tmp_path):
    """Test that OCR is used when standard PDF text extraction fails."""
    # Create a test PDF file
    test_file = tmp_path / "test_ocr.pdf"
    test_file.write_bytes(b"test pdf data")
    
    # Mock PyMuPDF for standard extraction (returning empty text)
    with patch('fitz.open') as mock_fitz_open:
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = ""  # Empty text to trigger OCR
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc
        
        # Mock PyPDF2 extraction (also returning empty text)
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            mock_reader = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = ""
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader
            
            # Mock EasyOCR
            with patch('easyocr.Reader') as mock_easyocr_reader:
                mock_reader = MagicMock()
                mock_reader.readtext.return_value = [("", "OCR extracted text", 0.9)]
                mock_easyocr_reader.return_value = mock_reader
                
                # Mock pdf2image
                with patch('pdf2image.convert_from_path') as mock_convert:
                    mock_img = MagicMock()
                    mock_convert.return_value = [mock_img]
                    
                    # Mock temp file operations
                    with patch('os.path.exists', return_value=True):
                        with patch('os.remove'):
                            
                            # Mock extract_data to return a DataFrame
                            with patch.object(parser, 'extract_data') as mock_extract_data:
                                mock_extract_data.return_value = pd.DataFrame({
                                    'qty': [100.00],
                                    'invoice_number': ['OCR-INVOICE'],
                                    'supplier_name': ['Feehily Supplier']
                                })
                                
                                # Call process_file method
                                result = parser.process_file(str(test_file))
                                
                                # Verify the result is a DataFrame with expected content
                                assert isinstance(result, pd.DataFrame)
                                assert 'invoice_number' in result.columns
                                assert result['invoice_number'].iloc[0] == 'OCR-INVOICE'
                                
                                # Verify OCR was used
                                mock_easyocr_reader.assert_called_once()
                                mock_reader.readtext.assert_called()
                                mock_convert.assert_called_once()

def test_ocr_not_used_when_standard_extraction_succeeds(parser, tmp_path):
    """Test that OCR is not used when standard PDF text extraction succeeds."""
    # Create a test PDF file
    test_file = tmp_path / "test_standard.pdf"
    test_file.write_bytes(b"test pdf data")
    
    # Mock PyMuPDF with successful text extraction
    with patch('fitz.open') as mock_fitz_open:
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Standard extracted text"  # Non-empty text
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc
        
        # Mock PyPDF2 - should not be called
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            # Mock EasyOCR - should not be called
            with patch('easyocr.Reader') as mock_easyocr_reader:
                # Mock pdf2image - should not be called
                with patch('pdf2image.convert_from_path') as mock_convert:
                    
                    # Mock extract_data to return a DataFrame
                    with patch.object(parser, 'extract_data') as mock_extract_data:
                        mock_extract_data.return_value = pd.DataFrame({
                            'qty': [200.00],
                            'invoice_number': ['STANDARD-INVOICE'],
                            'supplier_name': ['Standard Supplier']
                        })
                        
                        # Call process_file method
                        result = parser.process_file(str(test_file))
                        
                        # Verify the result is a DataFrame with expected content
                        assert isinstance(result, pd.DataFrame)
                        assert 'invoice_number' in result.columns
                        assert result['invoice_number'].iloc[0] == 'STANDARD-INVOICE'
                        
                        # Verify standard extraction was used
                        mock_fitz_open.assert_called_once()
                        mock_page.get_text.assert_called_once()
                        
                        # Verify OCR was not used
                        mock_pdf_reader.assert_not_called()
                        mock_easyocr_reader.assert_not_called()
                        mock_convert.assert_not_called()

def test_ocr_fallback_when_modules_not_available(tmp_path):
    """Test extraction when OCR-related modules are not available."""
    # Create parser with OCR disabled
    with patch('openai.OpenAI'):
        with patch('src.parsers.gpt_invoice_parser.PYPDF2_AVAILABLE', False):
            with patch('src.parsers.gpt_invoice_parser.EASYOCR_AVAILABLE', False):
                parser = GPTInvoiceParser(api_key="test_key")
                
                # Create a test PDF file
                test_file = tmp_path / "test_no_ocr.pdf"
                test_file.write_bytes(b"test pdf data")
                
                # Mock PyMuPDF with failed text extraction
                with patch('fitz.open') as mock_fitz_open:
                    mock_doc = MagicMock()
                    mock_page = MagicMock()
                    mock_page.get_text.return_value = ""  # Empty text to trigger OCR attempt
                    mock_doc.__iter__.return_value = [mock_page]
                    mock_fitz_open.return_value = mock_doc
                    
                    # Call process_file method
                    result = parser.process_file(str(test_file))
                    
                    # Since neither standard extraction works and OCR is unavailable,
                    # the method should return None
                    assert result is None

def test_handle_easyocr_exception(parser, tmp_path):
    """Test that exceptions during OCR processing are handled gracefully."""
    # Create a test PDF file
    test_file = tmp_path / "test_ocr_exception.pdf"
    test_file.write_bytes(b"test pdf data")
    
    # Mock PyMuPDF with failed text extraction
    with patch('fitz.open') as mock_fitz_open:
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = ""  # Empty text to trigger OCR
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc
        
        # Mock PyPDF2 extraction (also returning empty text)
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            mock_reader = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = ""
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader
            
            # Mock EasyOCR to raise an exception
            with patch('easyocr.Reader') as mock_easyocr_reader:
                mock_reader = MagicMock()
                mock_reader.readtext.side_effect = Exception("OCR processing error")
                mock_easyocr_reader.return_value = mock_reader
                
                # Mock pdf2image
                with patch('pdf2image.convert_from_path') as mock_convert:
                    mock_img = MagicMock()
                    mock_convert.return_value = [mock_img]
                    
                    # Call process_file method
                    result = parser.process_file(str(test_file))
                    
                    # Verify that the method returns None when OCR fails
                    assert result is None
                    
                    # Verify that OCR was attempted
                    mock_easyocr_reader.assert_called_once()
                    mock_reader.readtext.assert_called_once()
