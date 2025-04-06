"""Supplier-specific templates and field mappings for invoice processing."""

from typing import Dict, Any


# Mapping of supplier field names to standardized field names
FIELD_MAPPINGS = {
    "united_drug": {
        "QTY": "qty",
        "DESCRIPTION": "description",
        "PACK": "pack",
        "PRICE": "price",
        "INVOICE": "invoice_value",
        "INVOICE NO.": "invoice_number",
        "ACCOUNT": "account_number",
        "DATE": "invoice_date",
        "TIME": "invoice_time",
        "TYPE": "invoice_type",
        "CODE": "vat_code",
        "VAT%": "vat_rate_percent",
        "VAT": "vat_amount",
        "TOTAL": "total_amount",
        "YOUR REF.": "your_ref",
    },
    "genamed": {
        "Quantity": "qty",
        "Description": "description",
        "Unit Price": "price",
        "Amount": "invoice_value",
        "VAT": "vat_amount",
        "Total": "total_amount",
        "Invoice No:": "invoice_number",
        "PO Number:": "your_ref",
        "Invoice Date:": "invoice_date",
        "VAT Rate": "vat_rate_percent",
    },
    "iskus": {
        "QTY": "qty",
        "DESCRIPTION": "description",
        "PACK": "pack",
        "PRICE": "price",
        "DISC": "discount",
        "VAT": "vat",
        "INVOICE": "invoice_value",
        "INVOICE": "invoice_number",
        "ACCOUNT": "account_number",
        "DATE": "invoice_date",
        "TIME": "invoice_time",
        "TYPE": "invoice_type",
        "Batch:": "batch",
        "Expiry Date:": "expiry_date",
        "Our Ref:": "our_ref",
        "Your Ref:": "your_ref",
        "Delivery No.": "delivery_no",
    },
    "feehily": {
        "Qty": "qty",
        "Description": "description",
        "Pack": "pack",
        "Price": "price",
        "Value": "invoice_value",
        "Invoice No": "invoice_number",
        "Account No": "account_number",
        "Date": "invoice_date",
        "Time": "invoice_time",
    },
    "unknown": {
        # Default mappings for unknown suppliers
        "qty": "qty",
        "description": "description",
        "pack": "pack",
        "price": "price",
        "invoice_value": "invoice_value",
        "invoice_number": "invoice_number",
        "account_number": "account_number",
        "invoice_date": "invoice_date",
        "invoice_time": "invoice_time",
    }
}


# Supplier-specific prompts for GPT-4o
SUPPLIER_PROMPTS = {
    "united_drug": """
You are analyzing a United Drug invoice. These invoices typically have the following structure:
1. Header with invoice number, account, date, time, reference numbers
2. Line items with QTY, PACK, DESCRIPTION, PRICE, and INVOICE value columns
3. Footer with VAT information and totals

Please extract the following:
- All product line items with QTY, DESCRIPTION, PACK, PRICE, and INVOICE value
- Invoice metadata (invoice number, account, date, time, reference numbers)
- VAT information and totals

Note these specific characteristics of United Drug invoices:
- Line items typically start after the "QTY PACK DESCRIPTION" header
- The invoice number is usually found in the top section labeled "Invoice No."
- Dates are in DD.MM.YYYY format
- Some values may be in parentheses to indicate credits
    """,
    
    "genamed": """
You are analyzing a Genamed (NiAm Pharma) invoice. These invoices typically have the following structure:
1. Header with company information, invoice number, date and PO number
2. Line items with Unit, Description, Quantity, Unit Price, Amount, VAT and Total
3. Footer with totals and payment information

Please extract the following:
- All product line items with Quantity, Description, Unit Price, Amount, VAT and Total
- Invoice metadata (invoice number, date, PO number)
- Billing and shipping information

Note these specific characteristics of Genamed invoices:
- Line items may have detailed product descriptions over multiple lines
- Each line item often has batch numbers and expiry dates
- The invoice number is labeled as "Invoice No:"
- Dates are typically in DD-MM-YYYY format
    """,
    
    "iskus": """
You are analyzing an Iskus Health invoice. These invoices typically have the following structure:
1. Header with invoice number, account, date, time, reference numbers
2. Line items with QTY, DESCRIPTION, PACK, PRICE, DISC, VAT, and INVOICE value
3. Batch numbers and expiry dates for each product
4. Footer with totals

Please extract the following:
- All product line items with QTY, DESCRIPTION, PACK, PRICE, and INVOICE value
- Batch numbers and expiry dates for each product
- Invoice metadata (invoice number, account, date, time, reference numbers)
- VAT information and totals

Note these specific characteristics of Iskus invoices:
- Line items include batch numbers and expiry dates directly under each product
- The invoice number is in the top section, usually a 9-digit number starting with "97"
- Dates are in DD.MM.YYYY format
- The "Our Ref:", "Your Ref:", and "Delivery No." fields contain important reference numbers
    """,
    
    "feehily": """
You are analyzing a Feehily's invoice. These invoices typically have the following structure:
1. Header with invoice number, customer details, date
2. Line items with Qty, Description, Pack, Price, and Value columns
3. Footer with totals

Please extract the following:
- All product line items with Qty, Description, Pack, Price, and Value
- Invoice metadata (invoice number, account, date)
- Totals and VAT information

Note that Feehily's invoices may have minimal formatting or be challenging to parse due to scan quality.
    """,
    
    "unknown": """
You are analyzing an invoice from an unknown supplier. Please extract all structured data you can find, including:
1. All product line items with quantities, descriptions, and prices
2. Invoice metadata (invoice number, date, reference numbers)
3. Customer and supplier information
4. Totals, subtotals, and tax information

Pay special attention to tabular data, which likely represents the product line items.
    """
}


# Expected columns for each supplier type
EXPECTED_COLUMNS = {
    "united_drug": [
        "qty", "description", "pack", "price", "invoice_value", 
        "invoice_number", "account_number", "invoice_date", "invoice_time", 
        "invoice_type", "vat_code", "vat_rate_percent", "vat_amount", 
        "total_amount", "your_ref"
    ],
    "genamed": [
        "qty", "description", "price", "invoice_value", "vat_amount", 
        "total_amount", "invoice_number", "your_ref", "invoice_date", 
        "vat_rate_percent", "batch", "expiry_date"
    ],
    "iskus": [
        "qty", "description", "pack", "price", "discount", "vat", 
        "invoice_value", "invoice_number", "account_number", "invoice_date", 
        "invoice_time", "invoice_type", "batch", "expiry_date", "our_ref", 
        "your_ref", "delivery_no"
    ],
    "feehily": [
        "qty", "description", "pack", "price", "invoice_value", 
        "invoice_number", "account_number", "invoice_date", "invoice_time"
    ],
    "unknown": [
        "qty", "description", "pack", "price", "discount", "vat", 
        "invoice_value", "invoice_number", "account_number", "invoice_date", 
        "invoice_time", "total_amount"
    ]
}


# Post-processing functions for specific supplier types
def post_process_united_drug(df):
    """Post-process United Drug data."""
    # Specific processing for United Drug
    return df

def post_process_genamed(df):
    """Post-process Genamed data."""
    # Extract batch and expiry date from description if not already present
    if "description" in df.columns and "batch" not in df.columns:
        # Try to extract batch information
        df["batch"] = df["description"].str.extract(r"Batch:?\s*([A-Za-z0-9\-]+)")
    
    if "description" in df.columns and "expiry_date" not in df.columns:
        # Try to extract expiry date information
        df["expiry_date"] = df["description"].str.extract(r"Expiry Date:?\s*(\d{1,2}[\./-]\d{1,2}[\./-]\d{2,4})")
    
    return df

def post_process_iskus(df):
    """Post-process Iskus data."""
    # Iskus invoices often have batch and expiry info on separate lines
    # This is handled in the supplier's parser implementation
    return df

def post_process_feehily(df):
    """Post-process Feehily data."""
    # Feehily invoices might need special handling
    return df

def post_process_unknown(df):
    """Post-process unknown supplier data."""
    # Do basic cleanup
    return df

# Map supplier types to post-processing functions
POST_PROCESSORS = {
    "united_drug": post_process_united_drug,
    "genamed": post_process_genamed,
    "iskus": post_process_iskus,
    "feehily": post_process_feehily,
    "unknown": post_process_unknown
}


def get_prompt_template(supplier_type: str) -> str:
    """Get the prompt template for a specific supplier."""
    return SUPPLIER_PROMPTS.get(supplier_type, SUPPLIER_PROMPTS["unknown"])

def get_field_mapping(supplier_type: str) -> Dict[str, str]:
    """Get the field mapping for a specific supplier."""
    return FIELD_MAPPINGS.get(supplier_type, FIELD_MAPPINGS["unknown"])

def get_expected_columns(supplier_type: str) -> list:
    """Get the expected columns for a specific supplier."""
    return EXPECTED_COLUMNS.get(supplier_type, EXPECTED_COLUMNS["unknown"])

def get_post_processor(supplier_type: str):
    """Get the post-processing function for a specific supplier."""
    return POST_PROCESSORS.get(supplier_type, post_process_unknown)
