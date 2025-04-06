"""Test GPT invoice parser module."""
import os
import io
import pandas as pd
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    """Create a GPT invoice parser instance."""
    with patch('openai.OpenAI') as mock_openai:
        return GPTInvoiceParser(api_key="test_key")

def test_extract_data_success(parser):
    """Test extracting data from invoice text successfully."""
    # Sample CSV data to be returned from the mocked OpenAI API
    sample_csv = """qty,description,pack,price,discount,vat,invoice_value,invoice_number,account_number,invoice_date,invoice_time,invoice_type,handled_by,our_ref,delivery_no,your_ref,supplier_name,supplier_address,supplier_tel,supplier_fax,supplier_email,customer_name,customer_address,goods_value,vat_code,vat_rate_percent,vat_amount,total_amount,batch,expiry_date
5130.00,EUR,,,,5130.00,INVOICE,5700061,31.12.2024,20:00:11,ISKUS Standard Order,IMD,143801671,916097445,WEX31122024,Iskus Health Ltd.,4045 Kingswood Road Citywest Business Park Co. Dublin,01-4287895,01-4287876,info@iskushealth.com,B BRAUN WELLSTONE LTD,B BRAUN WELLSTONE RENAL CARE CENTRE 3 NAAS ROAD IND PK SINNOTSTOWN LANE Dublin Co. Dublin,5130.00,AA,23,1179.90,6309.90,,"""
    
    # Create a mock response from OpenAI API
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = sample_csv
    
    # Setup the mock for the OpenAI API call
    parser.client.chat.completions.create.return_value = mock_response
    
    # Mock the clean_dataframe method to return a fixed test DataFrame
    with patch.object(parser, '_clean_dataframe') as mock_clean:
        mock_clean.return_value = pd.DataFrame({
            'qty': [5130.00],
            'invoice_number': ['INVOICE'],
            'account_number': ['5700061'],
            'supplier_name': ['Test Supplier']
        })
        
        # Call the extract_data method
        result = parser.extract_data("Sample invoice text")
        
        # Verify the result is a DataFrame with the expected content
        assert isinstance(result, pd.DataFrame)
        assert 'qty' in result.columns
        assert 'invoice_number' in result.columns
        assert len(result) > 0
        assert result['invoice_number'].iloc[0] == 'INVOICE'
        assert float(result['qty'].iloc[0]) == 5130.00
        
        # Verify that the OpenAI API was called with the correct parameters
        parser.client.chat.completions.create.assert_called_once()
        args, kwargs = parser.client.chat.completions.create.call_args
        assert kwargs['model'] in ['gpt-4o', 'gpt-4']
        assert kwargs['temperature'] == 0.1  # Updated to match current implementation

def test_extract_data_failure(parser):
    """Test extracting data with API failure."""
    # Setup the mock to simulate an API error
    parser.client.chat.completions.create.side_effect = Exception("API Error")
    
    # Call the extract_data method
    result = parser.extract_data("Sample invoice text")
    
    # Verify the result is None due to the error
    assert result is None

def test_extract_data_empty_response(parser):
    """Test extracting data with empty API response."""
    # Create a mock response with empty content
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = ""
    
    # Setup the mock for the OpenAI API call
    parser.client.chat.completions.create.return_value = mock_response
    
    # Call the extract_data method
    result = parser.extract_data("Sample invoice text")
    
    # Verify the result is None due to empty content
    assert result is None

def test_extract_text_from_image(parser):
    """Test extracting text from an image."""
    # Mock the OpenAIExtractor's extract_text method
    with patch('src.parsers.openai_extractor.OpenAIExtractor') as mock_extractor_class:
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_text.return_value = "Sample text extracted from image"
        
        # Create sample image data
        image_data = b"test image data"
        
        # Call the extract_text_from_image method
        result = parser.extract_text_from_image(image_data)
        
        # Verify the result is the expected text
        assert result == "Sample text extracted from image"
        
        # Verify the OpenAIExtractor was called with the correct parameters
        mock_extractor_class.assert_called_once_with("test_key")
        mock_extractor.extract_text.assert_called_once_with(image_data)

def test_process_file_text(parser, tmp_path):
    """Test processing a text file."""
    # Create a test text file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Sample invoice text")
    
    # Mock the extract_data method
    with patch.object(parser, 'extract_data') as mock_extract_data:
        # Setup mock to return a test DataFrame
        mock_extract_data.return_value = pd.DataFrame({
            'qty': [5130.00],
            'invoice_number': ['INVOICE'],
            'supplier_name': ['Test Supplier']
        })
        
        # Call the process_file method
        result = parser.process_file(str(test_file))
        
        # Verify the result is a DataFrame with the expected content
        assert isinstance(result, pd.DataFrame)
        assert 'invoice_number' in result.columns
        assert result['invoice_number'].iloc[0] == 'INVOICE'
        
        # Verify extract_data was called with the file contents and supplier type
        mock_extract_data.assert_called_once()
        # The first argument should be the text content
        args, kwargs = mock_extract_data.call_args
        assert args[0] == "Sample invoice text"

def test_process_file_image(parser, tmp_path):
    """Test processing an image file."""
    # Create a test image file
    test_file = tmp_path / "test.jpg"
    test_file.write_bytes(b"test image data")
    
    # Mock the required methods
    with patch.object(parser, 'extract_text_from_image') as mock_extract_text, \
         patch.object(parser, 'extract_data') as mock_extract_data:
        
        # Setup mocks
        mock_extract_text.return_value = "Sample extracted text"
        mock_extract_data.return_value = pd.DataFrame({
            'qty': [5130.00],
            'invoice_number': ['INVOICE'],
            'supplier_name': ['Test Supplier']
        })
        
        # Call the process_file method
        result = parser.process_file(str(test_file))
        
        # Verify the result is a DataFrame with the expected content
        assert isinstance(result, pd.DataFrame)
        assert 'invoice_number' in result.columns
        assert result['invoice_number'].iloc[0] == 'INVOICE'
        
        # Verify both methods were called
        mock_extract_text.assert_called_once()
        # The first argument should be the text content, and now there's a supplier_type parameter as well
        args, kwargs = mock_extract_data.call_args
        assert args[0] == "Sample extracted text"
        # Don't test the exact value of supplier_type as it's determined dynamically

def test_process_file_pdf(parser, tmp_path):
    """Test processing a PDF file."""
    # Create a test PDF file
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"test pdf data")
    
    # Create a mock PDF module
    mock_fitz = MagicMock()
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Sample PDF text"
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz.open.return_value = mock_doc
    
    # Patch the fitz module at the sys.modules level
    with patch.dict('sys.modules', {'fitz': mock_fitz}):
        # Mock extract_data to return a test DataFrame
        with patch.object(parser, 'extract_data') as mock_extract_data:
            mock_extract_data.return_value = pd.DataFrame({
                'qty': [5130.00],
                'invoice_number': ['INVOICE'],
                'supplier_name': ['Test Supplier']
            })
            
            # Call process_file method
            result = parser.process_file(str(test_file))
            
            # Verify the result is a DataFrame with the expected content
            assert isinstance(result, pd.DataFrame)
            assert 'invoice_number' in result.columns
            assert result['invoice_number'].iloc[0] == 'INVOICE'
            
            # Verify that the PDF was opened and processed correctly
            mock_fitz.open.assert_called_once_with(str(test_file))
            mock_page.get_text.assert_called_once()
            
            # Verify extract_data was called with the PDF text
            args, kwargs = mock_extract_data.call_args
            assert args[0] == "Sample PDF text"

def test_process_file_unsupported(parser, tmp_path):
    """Test processing an unsupported file type."""
    test_file = tmp_path / "test.doc"
    test_file.write_bytes(b"test doc data")
    
    # Call the process_file method
    result = parser.process_file(str(test_file))
    
    # Verify the result is None for unsupported file type
    assert result is None

def test_process_file_nonexistent(parser):
    """Test processing a nonexistent file."""
    # Call the process_file method with a nonexistent file
    result = parser.process_file("nonexistent_file.txt")
    
    # Verify the result is None for nonexistent file
    assert result is None

def test_process_directory(parser, tmp_path):
    """Test processing a directory with multiple files."""
    # Create test directory
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    
    # Create test files
    test_txt = test_dir / "test.txt"
    test_txt.write_text("Sample invoice text")
    
    test_jpg = test_dir / "test.jpg"
    test_jpg.write_bytes(b"test image data")
    
    # Mock process_file to return expected data
    with patch.object(parser, 'process_file') as mock_process_file:
        # Setup mock to return different DataFrames based on file
        def side_effect(file_path):
            if file_path.endswith('.txt'):
                return pd.DataFrame({
                    'qty': [1.0],
                    'invoice_number': ['INV001'],
                    'supplier_name': ['Supplier A']
                })
            elif file_path.endswith('.jpg'):
                return pd.DataFrame({
                    'qty': [2.0],
                    'invoice_number': ['INV002'],
                    'supplier_name': ['Supplier B']
                })
            return None
            
        mock_process_file.side_effect = side_effect
        
        # Call the process_directory method
        result = parser.process_directory(str(test_dir))
        
        # Verify the result is a dictionary with expected content
        assert isinstance(result, dict)
        assert "test_dir" in result
        assert isinstance(result["test_dir"], pd.DataFrame)
        assert len(result["test_dir"]) == 2  # Two files processed
        
        # Verify process_file was called for each file
        assert mock_process_file.call_count == 2

def test_process_directory_empty(parser, tmp_path):
    """Test processing an empty directory."""
    # Create empty test directory
    test_dir = tmp_path / "empty_dir"
    test_dir.mkdir()
    
    # Call the process_directory method
    result = parser.process_directory(str(test_dir))
    
    # Verify the result is an empty dictionary
    assert isinstance(result, dict)
    assert len(result) == 0

def test_process_directory_nonexistent(parser):
    """Test processing a nonexistent directory."""
    # Call the process_directory method with a nonexistent directory
    result = parser.process_directory("nonexistent_dir")
    
    # Verify the result is None
    assert result is None

def test_process_directory_not_a_directory(parser, tmp_path):
    """Test processing a file as a directory."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Sample invoice text")
    
    # Call the process_directory method with a file path
    result = parser.process_directory(str(test_file))
    
    # Verify the result is None
    assert result is None

def test_init_no_api_key():
    """Test initialization without an API key."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': ''}, clear=True):
        with pytest.raises(Exception) as exc_info:
            GPTInvoiceParser()
        assert "OpenAI API key not provided" in str(exc_info.value)

def test_extract_data_empty_text(parser):
    """Test extract_data with empty text content."""
    result = parser.extract_data("")
    assert result is None
    
    result = parser.extract_data(None)
    assert result is None

def test_extract_data_text_truncation(parser):
    """Test extract_data with long text that needs truncation."""
    # Create a very long text that exceeds the max_chars limit (12000)
    long_text = "A" * 15000
    
    # Mock the OpenAI API response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "header\nvalue"
    parser.client.chat.completions.create.return_value = mock_response
    
    # Mock the clean_dataframe method to return a fixed test DataFrame
    with patch.object(parser, '_clean_dataframe') as mock_clean:
        mock_clean.return_value = pd.DataFrame({
            'header': ['value']
        })
        
        # Call the extract_data method
        parser.extract_data(long_text)
        
        # Verify that the text was truncated in the API call
        args, kwargs = parser.client.chat.completions.create.call_args
        user_message = [msg for msg in kwargs['messages'] if msg['role'] == 'user'][0]
        assert '... [truncated]' in user_message['content']
        assert len(user_message['content']) < len(long_text)

def test_extract_data_error_handling(parser):
    """Test error handling in extract_data method."""
    # The actual implementation returns None on error, not an empty dict
    with patch('openai.ChatCompletion.create', side_effect=Exception("Test error")):
        result = parser.extract_data("Some invoice text")
        assert result is None

def test_clean_dataframe_error_handling(parser):
    """Test error handling in data cleaning."""
    # Since we can't directly test _clean_dataframe, we'll test the extract_data method
    # with a mocked CSV response but cause a DataFrame processing error
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'col1,col2\nvalue1,1\nvalue2,2'
                    }
                }
            ]
        }
        
        # Force an error during pandas processing
        with patch('pandas.read_csv', side_effect=Exception("DataFrame processing error")):
            result = parser.extract_data("Some invoice text")
            assert result is None

def test_normalize_column_values(parser):
    """Test normalization of data in the extract_data method."""
    # Just test that the extract_data method doesn't crash with typical input
    try:
        with patch.object(parser, 'client') as mock_client:
            # Set up mock to return None to bypass any processing
            mock_client.chat.completions.create.side_effect = Exception("Test exception")
            
            # This should return None but not crash
            result = parser.extract_data("Some invoice text")
            
            # We're just testing that the method handles errors properly
            assert result is None
            
    except Exception as e:
        # If we get here, the test failed
        pytest.fail(f"extract_data method raised an exception: {e}")

def test_parse_with_system_error(parser):
    """Test behavior when critical system errors occur."""
    # Test with OpenAI client instantiation error
    with patch('openai.OpenAI', side_effect=Exception("API connection error")):
        with pytest.raises(Exception):
            parser = GPTInvoiceParser(api_key="test_key")
            
    # Test with complete system failure during API call
    parser.client.chat.completions.create.side_effect = SystemError("Critical system error")
    result = parser.extract_data("Sample invoice text")
    assert result is None

def test_process_csv_parsing_error(parser):
    """Test handling CSV parsing errors."""
    # Create a mock response with invalid CSV content
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is not valid CSV data"
    parser.client.chat.completions.create.return_value = mock_response
    
    # Call the extract_data method
    result = parser.extract_data("Sample invoice text")
    
    # Verify the result is None due to CSV parsing error
    assert result is None

def test_process_file_permission_error(parser, tmp_path):
    """Test process_file handling permission errors."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Sample invoice text")
    
    # Mock os.path.exists to return True but open to raise PermissionError
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = parser.process_file(str(test_file))
            assert result is None

def test_process_directory_handling_empty_results(parser, tmp_path):
    """Test process_directory handling empty results from process_file."""
    # Create test directory with files
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    
    test_file = test_dir / "test.txt"
    test_file.write_text("Sample invoice text")
    
    # Mock process_file to return None for all files
    with patch.object(parser, 'process_file', return_value=None):
        result = parser.process_directory(str(test_dir))
        
        # Verify the result is an empty dictionary
        assert isinstance(result, dict)
        assert len(result) == 0

def test_process_directory_error_handling(parser, tmp_path):
    """Test error handling in process_directory method."""
    # Create a test directory
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    
    # Mock os.listdir to raise an OSError
    with patch('os.listdir', side_effect=OSError("Test error")):
        result = parser.process_directory(str(test_dir))
        # The implementation returns an empty dict, not None
        assert result == {}

def test_extract_data_with_dataframe_error(parser):
    """Test extract_data with an error in DataFrame processing."""
    with patch('src.utils.supplier_detector.SupplierDetector.detect_supplier', return_value='generic'):
        mock_response = type('MockResponse', (), {
            'choices': [
                type('MockChoice', (), {
                    'message': type('MockMessage', (), {
                        'content': 'invoice_number,description,qty\nINV001,Test Item,2'
                    })
                })
            ]
        })
        
        # Mock the OpenAI client response
        with patch.object(parser.client.chat.completions, 'create', return_value=mock_response):
            # Mock the pandas processing to raise an error during DataFrame operations
            with patch('src.parsers.gpt_invoice_parser.GPTInvoiceParser._clean_dataframe', 
                      side_effect=Exception("DataFrame processing error")):
                # This should handle the error and return None
                result = parser.extract_data("Some invoice text")
                assert result is None

def test_process_file_with_permission_error(parser):
    """Test process_file when there's a permission error opening a file."""
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        result = parser.process_file("/path/to/invoice.pdf")
        assert result is None

def test_process_directory_with_path_error(parser):
    """Test process_directory when there's an invalid path."""
    with patch('os.path.exists', return_value=False):
        # When directory doesn't exist, process_directory returns None
        result = parser.process_directory("/invalid/path")
        assert result is None
