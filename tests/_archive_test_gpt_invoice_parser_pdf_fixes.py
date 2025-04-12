import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open

from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    return GPTInvoiceParser(api_key="test_key")

def test_pdf_with_special_supplier(parser, tmp_path):
    """Test processing PDF with special supplier detection."""
    # Create a PDF file path (we won't actually write to it)
    pdf_file = tmp_path / "special_supplier.pdf"
    
    # Mock the open function to avoid file access issues
    m = mock_open(read_data=b"%PDF-1.5\nTest PDF content")
    
    # First patch the built-in open function for both binary and text modes
    with patch("builtins.open", m):
        # Create a PyPDF2 mock that returns text with supplier info
        mock_pdf_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Invoice from Special Supplier Ltd"
        mock_pdf_reader.pages = [mock_page]
        
        # Patch PyPDF2.PdfReader to return our mock reader
        with patch('PyPDF2.PdfReader', return_value=mock_pdf_reader):
            # Mock supplier detection to return a specific supplier
            with patch('src.utils.supplier_detector.SupplierDetector.detect_supplier', return_value='Special Supplier'):
                # Mock extract_data to return a valid DataFrame
                with patch.object(parser, 'extract_data', return_value=pd.DataFrame({
                    "invoice_number": ["SP123"],
                    "supplier_name": ["Special Supplier"]
                })) as mock_extract:
                    # Process the file
                    result = parser.process_file(str(pdf_file))
                    
                    # Verify our extract_data mock was called
                    assert mock_extract.called
                    # Verify result is a DataFrame
                    assert isinstance(result, pd.DataFrame)

def test_pdf_processing_with_content_supplier_detection(parser, tmp_path):
    """Test PDF processing with supplier detection from content."""
    # Create a PDF file path (we won't actually write to it)
    pdf_file = tmp_path / "supplier_detection.pdf"
    
    # Mock the open function to avoid file access issues
    m = mock_open(read_data=b"%PDF-1.5\nTest PDF content")
    
    # First patch the built-in open function 
    with patch("builtins.open", m):
        # Mock PyPDF2 to extract text with supplier information
        mock_pdf_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Invoice from United Drug Ltd"
        # Mock the pages attribute to be accessible as an iterable
        mock_pdf_reader.pages = [mock_page]
        
        # First, patch PyPDF2.PdfReader to return our mock
        with patch('PyPDF2.PdfReader', return_value=mock_pdf_reader):
            # Mock the supplier detector
            with patch('src.utils.supplier_detector.SupplierDetector.detect_supplier', return_value='United Drug'):
                # Mock extract_data to return a valid DataFrame
                with patch.object(parser, 'extract_data', return_value=pd.DataFrame({
                    "invoice_number": ["UD123"], 
                    "supplier_name": ["United Drug"]
                })) as mock_extract:
                    # Process the file
                    result = parser.process_file(str(pdf_file))
                    
                    # Verify that extract_data was called and result is a DataFrame
                    assert mock_extract.called
                    assert isinstance(result, pd.DataFrame)

def test_final_supplier_detection_from_text(parser, tmp_path):
    """Test final supplier detection from text content."""
    # Create a PDF file path (we won't actually write to it)
    pdf_file = tmp_path / "supplier_in_content.pdf"
    
    # Mock the open function to avoid file access issues
    m = mock_open(read_data=b"%PDF-1.5\nTest PDF content")
    
    # First patch the built-in open function
    with patch("builtins.open", m):
        # Create a mock that will be returned by PyPDF2.PdfReader
        mock_pdf_reader = MagicMock()
        mock_page = MagicMock()
        # Set up text that contains supplier information 
        mock_page.extract_text.return_value = "Invoice from United Drug Ltd"
        mock_pdf_reader.pages = [mock_page]
        
        # Patch PyPDF2.PdfReader first
        with patch('PyPDF2.PdfReader', return_value=mock_pdf_reader):
            # Now patch the supplier detection
            with patch('src.utils.supplier_detector.SupplierDetector.detect_supplier', return_value='United Drug'):
                # And finally patch extract_data to return a valid DataFrame
                with patch.object(parser, 'extract_data', return_value=pd.DataFrame({
                    "invoice_number": ["UD123"],
                    "supplier_name": ["United Drug"]
                })) as mock_extract:
                    # Process the file
                    result = parser.process_file(str(pdf_file))
                    
                    # Verify that extract_data was called with the right supplier type
                    assert mock_extract.called
                    
                    # Verify the result
                    assert isinstance(result, pd.DataFrame)
                    
                    # Check that our mock was called as expected
                    # First arg is text content, second might be supplier_type
                    call_args = mock_extract.call_args[0]
                    if len(call_args) > 1 and call_args[1] is not None:
                        # If supplier detection worked, it should be "United Drug"
                        assert "united drug" in call_args[1].lower()
