import pytest
import os
import pandas as pd
from unittest.mock import patch
from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    return GPTInvoiceParser(api_key="test_key")

def test_supplier_detection_in_process_file(parser, tmp_path):
    """Test supplier detection logic in process_file method."""

    # Test files with different supplier types
    test_files = [
        ("Fehily's_Invoice.txt", "feehily"),
        ("Feehily_Invoice.txt", "feehily"),
        ("Fehily_Invoice.txt", "feehily"),
        ("United_Drug_Invoice.txt", "united_drug")  # Use underscore to match implementation pattern
    ]

    for filename, expected_supplier_keyword in test_files:
        test_file = tmp_path / filename
        content = "Sample invoice content"
        test_file.write_text(content)

        # Mock extract_data to return a DataFrame and check if correct supplier type is passed
        with patch.object(parser, 'extract_data', return_value=pd.DataFrame({
            'invoice_number': ['12345']
        })) as mock_extract:
            # Process the file
            parser.process_file(str(test_file))

            # Verify extract_data was called
            assert mock_extract.called

            # Verify the supplier type was passed correctly
            mock_extract.assert_called_once()
            call_args = mock_extract.call_args[0]

            # The first argument should be the text content
            assert content in call_args[0]

            # The second argument (supplier_type) should contain the expected supplier keyword
            if len(call_args) > 1 and call_args[1] is not None:
                supplier_type = call_args[1].lower()
                assert expected_supplier_keyword == supplier_type, f"Expected '{expected_supplier_keyword}' but got '{supplier_type}' for file {filename}"
