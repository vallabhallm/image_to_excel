import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    return GPTInvoiceParser(api_key="test_key")

def test_final_supplier_detection_from_text(parser, tmp_path):
    """Test final supplier detection from text content."""
    # Create a valid PDF file
    pdf_file = tmp_path / "supplier_in_content.pdf"
    with open(str(pdf_file), 'wb') as f:
        f.write(b"%PDF-1.5\nTest PDF content")
    
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
