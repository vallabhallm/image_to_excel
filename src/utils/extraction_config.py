"""Configuration for extraction patterns and rules.

This module contains regex patterns and extraction rules used by parsers.
Centralizing these patterns allows for easier maintenance and configuration.
"""

# Constants for extraction rules
ADDRESS_MAX_LINES = 5
SUPPLIER_HEADER_LINES = 1
INVOICE_ITEM_MIN_LENGTH = 3

# Regex patterns for contact information
TELEPHONE_PATTERNS = [
    r"Tel(?:ephone)?:?\s*([0-9\-\+\(\)\s]+)",
    r"Phone:?\s*([0-9\-\+\(\)\s]+)",
    r"T:?\s*([0-9\-\+\(\)\s]+)"
]

FAX_PATTERNS = [
    r"Fax:?\s*([0-9\-\+\(\)\s]+)",
    r"F:?\s*([0-9\-\+\(\)\s]+)"
]

EMAIL_PATTERNS = [
    r"Email:?\s*([^\s,]+@[^\s,]+\.[^\s,]+)",
    r"E-?mail:?\s*([^\s,]+@[^\s,]+\.[^\s,]+)",
    r"E:?\s*([^\s,]+@[^\s,]+\.[^\s,]+)",
    r"([^\s,]+@[^\s,]+\.[^\s,]+)"  # Generic email pattern as fallback
]

# Patterns for invoice details
INVOICE_NUMBER_PATTERNS = [
    r"Invoice\s*(?:#|No|Number|Reference)(?:\s*:|\.)?(?:\s*)([A-Za-z0-9\-\/]+)",
    r"Invoice:?\s*([A-Za-z0-9\-\/]+)",
    r"INV(?:OICE)?\s*(?:#|No|Number)?(?:\s*:|\.)?(?:\s*)([A-Za-z0-9\-\/]+)"
]

DATE_PATTERNS = [
    r"(?:Invoice)?\s*Date:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
    r"(?:Invoice)?\s*Date:?\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*\d{2,4})",
    r"Date:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
    r"Date:?\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*\d{2,4})",
    r"Date:?\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?[\s,]*\d{2,4})"
]

PO_NUMBER_PATTERNS = [
    r"(?:Purchase\s*Order|PO|P\.O\.|Order)\s*(?:#|No|Number|Reference)?(?:\s*:|\.)?(?:\s*)([A-Za-z0-9\-\/]+)",
    r"(?:Your|Customer)\s*(?:PO|Order)(?:\s*#|No)?:?\s*([A-Za-z0-9\-\/]+)"
]

# Patterns for financial details
SUBTOTAL_PATTERNS = [
    r"(?:Sub[- ]?total|Total before tax):?\s*(?:£|\$|€|USD|GBP|EUR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
    r"(?:Sub[- ]?total|Total before tax):?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:£|\$|€|USD|GBP|EUR)?",
]

TAX_PATTERNS = [
    r"(?:VAT|Tax|GST|HST):?\s*(?:£|\$|€|USD|GBP|EUR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
    r"(?:VAT|Tax|GST|HST):?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:£|\$|€|USD|GBP|EUR)?",
]

TOTAL_PATTERNS = [
    r"(?:Total|Grand Total|Amount Due|Balance Due):?\s*(?:£|\$|€|USD|GBP|EUR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
    r"(?:Total|Grand Total|Amount Due|Balance Due):?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:£|\$|€|USD|GBP|EUR)?",
]

# Patterns for customer information
CUSTOMER_SECTION_PATTERNS = [
    r"(?:Customer|Client|Bill To|Ship To|Deliver To|Sold To|Recipient)(?:\s*:|\s+Information\s*:)?(.*?)(?=Invoice\s|Date\s|Order\s|Delivery|Payment)",
    r"(?:Customer|Client|Bill To|Ship To|Deliver To|Sold To|Recipient)(?:[:\s]*)([^\n]+(?:\n[^\n]+){0,5})"
]

# Patterns for batch and expiry information
BATCH_PATTERNS = [
    r"(?:Batch|Lot)(?:\s+No)?(?:[\s.:]*)([\w\-]+)",
    r"(?:Batch|Lot)(?:\s+Number)?(?:[\s.:]*)([\w\-]+)"
]

EXPIRY_PATTERNS = [
    r"(?:Expiry|Expiration|Exp|Expiry Date|Expiration Date)(?:[\s.:]*)([\d\/\-\.]+)",
    r"(?:Expiry|Expiration|Exp|Expiry Date|Expiration Date)(?:[\s.:]*)((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s.]*\d{1,2}[\s,]*\d{2,4})"
]

# Section identification markers
SUPPLIER_SECTION_END_MARKERS = [
    "Email:", "Fax:", "Tel:", "VAT Reg"
]

INVOICE_SECTION_START_MARKERS = [
    "INVOICE", "Invoice", "Date:", "Invoice Number:"
]

# Item extraction patterns
ITEM_HEADER_PATTERNS = [
    r"QTY\s+DESCRIPTION\s+(?:UNIT\s+)?PRICE\s+AMOUNT",
    r"QUANTITY\s+ITEM\s+(?:UNIT\s+)?PRICE\s+(?:DISC\s+)?(?:VAT\s+)?AMOUNT",
    r"QTY\s+ITEM\s+(?:UNIT\s+)?PRICE\s+(?:DISC\s+)?(?:VAT\s+)?AMOUNT",
]

ITEM_SECTION_END_MARKERS = [
    "SUBTOTAL", "Subtotal", "TOTAL", "Total", "VAT", "Tax"
]

# Item format patterns
ITEM_QTY_PATTERNS = [
    r"^\s*(\d+(?:\.\d+)?)\s+",
    r"^\s*(\d+)__"
]
