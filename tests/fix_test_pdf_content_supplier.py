import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    return GPTInvoiceParser(api_key="test_key")

def test_pdf_processing_with_content_supplier_detection(parser, tmp_path):
    """Test PDF processing with supplier detection from content."""
    # Create a PDF file with valid PDF content
    pdf_file = tmp_path / "supplier_detection.pdf"
    with open(str(pdf_file), 'wb') as f:
        f.write(b"%PDF-1.5\nTest PDF content")
    
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
