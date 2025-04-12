import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    return GPTInvoiceParser(api_key="test_key")

def test_pdf_with_special_supplier(parser, tmp_path):
    """Test processing PDF with special supplier detection."""
    # Create a PDF file with valid PDF header
    pdf_file = tmp_path / "special_supplier.pdf"
    pdf_file.write_bytes(b"%PDF-1.5\nTest PDF content")
    
    # Create a PyPDF2 mock that returns text with supplier info
    mock_pdf_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Invoice from Special Supplier Ltd"
    mock_pdf_reader.pages = [mock_page]
    
    # First patch PyPDF2.PdfReader to return our mock reader
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
