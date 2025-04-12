import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    return GPTInvoiceParser(api_key="test_key")

def test_pymupdf_extraction(parser, tmp_path):
    """Test fitz (PyMuPDF) PDF extraction."""
    # Create a valid PDF file
    pdf_file = tmp_path / "test_pymupdf.pdf"
    pdf_file.write_bytes(b"%PDF-1.5\nTest content")
    
    # Mock PyPDF2 to fail first (this will cause PyMuPDF to be used as fallback)
    with patch('PyPDF2.PdfReader', side_effect=Exception("PyPDF2 error")):
        # Mock fitz (PyMuPDF) document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Extracted text from PyMuPDF"
        # Use __iter__ to make it iterable (needed if the code loops through pages)
        mock_doc.__iter__.return_value = [mock_page]
        # Also support direct indexing which might be used
        mock_doc.__getitem__.return_value = mock_page
        # Set length if needed
        mock_doc.__len__.return_value = 1
        
        # Now patch fitz.open to return our mock document
        with patch('fitz.open', return_value=mock_doc):
            # Mock extract_data to return a valid DataFrame
            with patch.object(parser, 'extract_data', return_value=pd.DataFrame({"invoice_number": ["PDF123"]})) as mock_extract:
                # Process the file
                result = parser.process_file(str(pdf_file))
                
                # Verify our mocks were called correctly
                assert mock_extract.called
                assert isinstance(result, pd.DataFrame)
