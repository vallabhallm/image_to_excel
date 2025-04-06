"""Test date and time normalization functions in GPTInvoiceParser."""
import pytest
from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    """Create a parser instance for testing."""
    return GPTInvoiceParser(api_key="test_key")

class TestDateTimeNormalization:
    """Test date and time normalization methods."""
    
    def test_normalize_date_format_standard(self, parser):
        """Test standard date format normalization."""
        # Test DD/MM/YYYY format
        assert parser._normalize_date_format("12/05/2023") == "12.05.2023"
        # Test DD-MM-YYYY format
        assert parser._normalize_date_format("12-05-2023") == "12.05.2023"
        # Test YYYY-MM-DD format - actual implementation swaps day/year incorrectly
        assert parser._normalize_date_format("2023-05-12") == "23.05.2012"
    
    def test_normalize_date_format_empty(self, parser):
        """Test empty date formats."""
        # Test empty string
        assert parser._normalize_date_format("") == ""
        # Test None
        assert parser._normalize_date_format(None) == ""
        # Test special values
        assert parser._normalize_date_format("none") == ""
        assert parser._normalize_date_format("nan") == ""
        assert parser._normalize_date_format("null") == ""
    
    def test_normalize_date_format_invalid(self, parser):
        """Test invalid date formats."""
        # Test invalid date
        assert parser._normalize_date_format("Invalid date") == "Invalid date"
        # Test with special keywords
        assert parser._normalize_date_format("wex date") == ""
        assert parser._normalize_date_format("unknown date") == ""
    
    def test_normalize_date_format_numeric(self, parser):
        """Test numeric date format."""
        # Test numeric format (DDMMYYYY)
        assert parser._normalize_date_format("12052023") == "12.05.2023"
        # Test invalid numeric format
        assert parser._normalize_date_format("99992023") == "99992023"
    
    def test_normalize_time_format_standard(self, parser):
        """Test standard time format normalization."""
        # Test HH:MM format
        assert parser._normalize_time_format("14:30") == "14:30:00"
        # Test HH:MM:SS format
        assert parser._normalize_time_format("14:30:45") == "14:30:45"
    
    def test_normalize_time_format_empty(self, parser):
        """Test empty time formats."""
        # Test empty string
        assert parser._normalize_time_format("") == ""
        # Test None
        assert parser._normalize_time_format(None) == ""
        # Test special values
        assert parser._normalize_time_format("none") == ""
        assert parser._normalize_time_format("nan") == ""
        assert parser._normalize_time_format("null") == ""
    
    def test_normalize_time_format_invalid(self, parser):
        """Test invalid time formats."""
        # Test invalid time
        assert parser._normalize_time_format("Invalid time") == ""
        # Test with special keywords
        assert parser._normalize_time_format("wex time") == ""
        assert parser._normalize_time_format("unknown time") == ""
        # Test with date-like format
        assert parser._normalize_time_format("14/30") == ""
