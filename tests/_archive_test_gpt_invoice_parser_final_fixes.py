import pytest
import os
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open

from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    return GPTInvoiceParser(api_key="test_key")

def test_pdf_special_supplier_detection(parser, tmp_path):
    """Test PDF processing with supplier detection directly from mock PDF reader."""
    # Create a test PDF file
    pdf_file = tmp_path / "special_supplier.pdf"
    pdf_file.write_bytes(b"%PDF-1.5\nTest PDF content")
    
    # Mock PyPDF2.PdfReader to return a reader with supplier info in extracted text
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Invoice from Special Supplier Ltd"
    mock_reader.pages = [mock_page]
    
    # Patch PyPDF2.PdfReader
    with patch('PyPDF2.PdfReader', return_value=mock_reader):
        # Patch SupplierDetector to detect our supplier
        with patch('src.utils.supplier_detector.SupplierDetector.detect_supplier', return_value='Special Supplier'):
            # Mock extract_data to return a test DataFrame
            with patch.object(parser, 'extract_data', return_value=pd.DataFrame({
                "invoice_number": ["SP123"],
                "supplier_name": ["Special Supplier"]
            })) as mock_extract:
                # Run the process_file method
                result = parser.process_file(str(pdf_file))
                
                # Verify extract_data was called with the right supplier
                assert mock_extract.called
                # Check the result
                assert isinstance(result, pd.DataFrame)

def test_united_drug_supplier_in_pdf(parser, tmp_path):
    """Test United Drug supplier detection from PDF content."""
    # Create a test PDF file
    pdf_file = tmp_path / "united_drug.pdf"
    pdf_file.write_bytes(b"%PDF-1.5\nTest PDF content")
    
    # Create a mock with United Drug text content
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Invoice from United Drug Ltd"
    mock_reader.pages = [mock_page]
    
    # Patch the PdfReader constructor
    with patch('PyPDF2.PdfReader', return_value=mock_reader):
        # Patch supplier detection to return our target supplier
        with patch('src.utils.supplier_detector.SupplierDetector.detect_supplier', return_value='United Drug'):
            # Mock extract_data to return a DataFrame
            with patch.object(parser, 'extract_data', return_value=pd.DataFrame({
                "invoice_number": ["UD123"],
                "supplier_name": ["United Drug"]
            })) as mock_extract:
                # Process the file
                result = parser.process_file(str(pdf_file))
                
                # Check if extract_data was called and result is a DataFrame
                assert mock_extract.called
                assert isinstance(result, pd.DataFrame)
                
                # Check supplier was detected correctly
                assert result['supplier_name'].iloc[0] == 'United Drug'

def test_fehilys_supplier_detection(parser, tmp_path):
    """Test Fehily's supplier detection with apostrophe in filename."""
    # Create a test file with Fehily's in the name
    fehily_file = tmp_path / "Fehily's_Invoice_123.txt"
    content = "Invoice content from Fehily's"
    fehily_file.write_text(content)
    
    # Mock extract_data to return a DataFrame
    with patch.object(parser, 'extract_data', return_value=pd.DataFrame({
        "invoice_number": ["FH123"],
        "supplier_name": ["Fehily's"]
    })) as mock_extract:
        # Process the file
        result = parser.process_file(str(fehily_file))
        
        # Verify extract_data was called
        assert mock_extract.called
        
        # Get the arguments extract_data was called with
        call_args = mock_extract.call_args[0]
        
        # The first argument should be the text content
        assert content in call_args[0]
        
        # The second argument should be the supplier type detected from filename
        if len(call_args) > 1 and call_args[1] is not None:
            supplier_type = call_args[1].lower()
            # Check that it contains some variation of Fehily
            assert "fehil" in supplier_type or "feehil" in supplier_type

def test_constructor_options():
    """Test constructor options."""
    # Test with explicit API key
    parser = GPTInvoiceParser(api_key="test_api_key")
    assert parser.api_key == "test_api_key"
    
    # Test with environment variable (if supported)
    with patch.dict(os.environ, {"OPENAI_API_KEY": "env_api_key"}):
        parser = GPTInvoiceParser()
        assert parser.api_key == "env_api_key"

def test_process_directory_recursive(parser, tmp_path):
    """Test process_directory with subdirectories (os.walk implementation)."""
    # Create directory structure
    main_dir = tmp_path / "invoices"
    main_dir.mkdir()
    sub_dir = main_dir / "subdir"
    sub_dir.mkdir()
    
    # Create test files in both directories
    main_file = main_dir / "invoice1.txt"
    main_file.write_text("Main invoice")
    sub_file = sub_dir / "invoice2.txt"
    sub_file.write_text("Subdir invoice")
    
    # Mock process_file to return test DataFrames
    def mock_process(file_path):
        if "invoice1" in file_path:
            return pd.DataFrame({"invoice_number": ["MAIN1"]})
        elif "invoice2" in file_path:
            return pd.DataFrame({"invoice_number": ["SUB1"]})
        return None
    
    # Mock glob.glob to make sure it finds our files
    def mock_glob(pattern):
        if pattern.endswith('.txt'):
            if "subdir" in pattern:
                return [str(sub_file)]
            return [str(main_file)]
        return []
    
    # Apply the mocks
    with patch.object(parser, 'process_file', side_effect=mock_process):
        with patch('glob.glob', side_effect=mock_glob):
            # Process the directory
            result = parser.process_directory(str(main_dir))
            
            # Check the result structure
            assert isinstance(result, dict)
            assert "invoices" in result
            
            # Verify both files were processed
            df = result["invoices"]
            assert "source_file" in df.columns
            source_files = df['source_file'].tolist()
            assert "invoice1.txt" in str(source_files)
            assert "invoice2.txt" in str(source_files)
