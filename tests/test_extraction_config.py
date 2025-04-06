"""Test extraction configuration module."""
import re
import pytest
from src.utils import extraction_config as config


def test_config_constants():
    """Test that configuration constants are defined correctly."""
    assert isinstance(config.ADDRESS_MAX_LINES, int)
    assert config.ADDRESS_MAX_LINES > 0
    assert isinstance(config.SUPPLIER_HEADER_LINES, int)
    assert config.SUPPLIER_HEADER_LINES > 0
    assert isinstance(config.INVOICE_ITEM_MIN_LENGTH, int)
    assert config.INVOICE_ITEM_MIN_LENGTH > 0


def test_telephone_patterns():
    """Test that telephone patterns match expected formats."""
    assert isinstance(config.TELEPHONE_PATTERNS, list)
    assert len(config.TELEPHONE_PATTERNS) > 0
    
    # Test some valid telephone number formats
    test_texts = [
        "Tel: +1 (555) 123-4567",
        "Telephone: 555-123-4567",
        "Phone: 5551234567",
        "T: +44 20 7123 4567"
    ]
    
    for text in test_texts:
        matches = False
        for pattern in config.TELEPHONE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matches = True
                break
        assert matches, f"Pattern should match: {text}"


def test_email_patterns():
    """Test that email patterns match expected formats."""
    assert isinstance(config.EMAIL_PATTERNS, list)
    assert len(config.EMAIL_PATTERNS) > 0
    
    # Test some valid email formats
    test_texts = [
        "Email: test@example.com",
        "E-mail: support@company.co.uk",
        "E: info@domain.org",
        "Contact us at sales@business.net"
    ]
    
    for text in test_texts:
        matches = False
        for pattern in config.EMAIL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matches = True
                break
        assert matches, f"Pattern should match: {text}"


def test_invoice_number_patterns():
    """Test that invoice number patterns match expected formats."""
    assert isinstance(config.INVOICE_NUMBER_PATTERNS, list)
    assert len(config.INVOICE_NUMBER_PATTERNS) > 0
    
    # Test some valid invoice number formats
    test_texts = [
        "Invoice #: INV-2023-001",
        "Invoice No.: 10057893",
        "Invoice Number: ABC/12345",
        "Invoice: 2023-05-001",
        "INV #: 123456"
    ]
    
    for text in test_texts:
        matches = False
        for pattern in config.INVOICE_NUMBER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1):
                matches = True
                break
        assert matches, f"Pattern should match: {text}"


def test_date_patterns():
    """Test that date patterns match expected formats."""
    assert isinstance(config.DATE_PATTERNS, list)
    assert len(config.DATE_PATTERNS) > 0
    
    # Test some valid date formats
    test_texts = [
        "Invoice Date: 01/15/2023",
        "Date: 15-01-2023",
        "Date: 15.01.2023",
        "Date: 15th January 2023",
        "Date: Jan 15, 2023"
    ]
    
    for text in test_texts:
        matches = False
        for pattern in config.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1):
                matches = True
                break
        assert matches, f"Pattern should match: {text}"


def test_financial_patterns():
    """Test that financial amount patterns match expected formats."""
    # Test subtotal patterns
    assert isinstance(config.SUBTOTAL_PATTERNS, list)
    assert len(config.SUBTOTAL_PATTERNS) > 0
    
    # Test total patterns
    assert isinstance(config.TOTAL_PATTERNS, list)
    assert len(config.TOTAL_PATTERNS) > 0
    
    # Test some valid financial amounts
    test_texts = [
        "Subtotal: $100.00",
        "Sub-total: 100.00",
        "Total before tax: EUR 100.00",
        "VAT: £20.00",
        "Tax: 20.00",
        "GST: $10.50",
        "Total: 120.00",
        "Grand Total: USD 120.00",
        "Amount Due: $120.00"
    ]
    
    all_patterns = (
        config.SUBTOTAL_PATTERNS + 
        config.TAX_PATTERNS + 
        config.TOTAL_PATTERNS
    )
    
    for text in test_texts:
        matches = False
        for pattern in all_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1):
                matches = True
                break
        assert matches, f"Some financial pattern should match: {text}"


def test_item_patterns():
    """Test that item patterns match expected formats."""
    # Test item header patterns
    assert isinstance(config.ITEM_HEADER_PATTERNS, list)
    assert len(config.ITEM_HEADER_PATTERNS) > 0
    
    # Test item quantity patterns
    assert isinstance(config.ITEM_QTY_PATTERNS, list)
    assert len(config.ITEM_QTY_PATTERNS) > 0
    
    # Test some valid item headers
    header_texts = [
        "QTY DESCRIPTION PRICE AMOUNT",
        "QUANTITY ITEM UNIT PRICE AMOUNT",
        "QTY ITEM PRICE DISC VAT AMOUNT"
    ]
    
    for text in header_texts:
        matches = False
        for pattern in config.ITEM_HEADER_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matches = True
                break
        assert matches, f"Item header pattern should match: {text}"
    
    # Test some valid item quantity formats
    qty_texts = [
        "5 Widget A",
        "10.5 Service hours",
        "3__ Premium Widget"
    ]
    
    for text in qty_texts:
        matches = False
        for pattern in config.ITEM_QTY_PATTERNS:
            match = re.match(pattern, text)
            if match and match.group(1):
                matches = True
                break
        assert matches, f"Item quantity pattern should match: {text}"


def test_batch_and_expiry_patterns():
    """Test that batch and expiry patterns match expected formats."""
    # Test batch patterns
    assert isinstance(config.BATCH_PATTERNS, list)
    assert len(config.BATCH_PATTERNS) > 0
    
    # Test expiry patterns
    assert isinstance(config.EXPIRY_PATTERNS, list)
    assert len(config.EXPIRY_PATTERNS) > 0
    
    # Test some valid batch formats
    batch_texts = [
        "Batch: ABC123",
        "Lot No: XYZ-456",
        "Batch No: 20230501-A"
    ]
    
    for text in batch_texts:
        matches = False
        for pattern in config.BATCH_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1):
                matches = True
                break
        assert matches, f"Batch pattern should match: {text}"
    
    # Test some valid expiry formats
    expiry_texts = [
        "Expiry: 01/05/2025",
        "Expiration Date: 2025-05-01",
        "Exp: May 1, 2025"
    ]
    
    for text in expiry_texts:
        matches = False
        for pattern in config.EXPIRY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1):
                matches = True
                break
        assert matches, f"Expiry pattern should match: {text}"


def test_section_markers():
    """Test that section markers are defined correctly."""
    # Test supplier section end markers
    assert isinstance(config.SUPPLIER_SECTION_END_MARKERS, list)
    assert len(config.SUPPLIER_SECTION_END_MARKERS) > 0
    
    # Test invoice section start markers
    assert isinstance(config.INVOICE_SECTION_START_MARKERS, list)
    assert len(config.INVOICE_SECTION_START_MARKERS) > 0
    
    # Test item section end markers
    assert isinstance(config.ITEM_SECTION_END_MARKERS, list)
    assert len(config.ITEM_SECTION_END_MARKERS) > 0
