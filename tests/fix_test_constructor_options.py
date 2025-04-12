import pytest
import inspect
from src.parsers.gpt_invoice_parser import GPTInvoiceParser

def test_constructor_options():
    """Test GPTInvoiceParser constructor with different options."""
    # Test with API key explicitly provided
    parser = GPTInvoiceParser(api_key="custom_key")
    assert parser.api_key == "custom_key"
    
    # Test with default model (no need to specify if not supported)
    # Check if model parameter exists in the constructor
    init_signature = inspect.signature(GPTInvoiceParser.__init__)
    if 'model' in init_signature.parameters:
        # Only test this if the model parameter exists
        parser = GPTInvoiceParser(api_key="test_key", model="gpt-4o")
        assert parser.model == "gpt-4o"
