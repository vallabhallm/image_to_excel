#!/usr/bin/env python3
"""
Script to extract structured data from invoice text using GPT-4o.
This can be run standalone or imported as a module.
"""
import sys
import pandas as pd
from loguru import logger
from src.parsers.gpt_invoice_parser import GPTInvoiceParser
from src.utils.config_manager import ConfigManager

def extract_invoice_data(invoice_text):
    """Extract structured data from invoice text using GPT-4o.
    
    Args:
        invoice_text: Raw text from invoice
        
    Returns:
        DataFrame containing structured invoice data
    """
    try:
        # Get API key from config
        config = ConfigManager()
        api_key = config.get('openai', 'api_key')
        if not api_key:
            logger.error("OpenAI API key not found in configuration")
            return None
            
        parser = GPTInvoiceParser(api_key)
        df = parser.extract_data(invoice_text)
        
        if df is None:
            logger.error("Failed to parse invoice text")
            return None
        
        # Ensure all expected columns are present (even if empty)
        expected_columns = [
            'qty', 'description', 'pack', 'price', 'discount', 'vat', 'invoice_value',
            'invoice_number', 'account_number', 'invoice_date', 'invoice_time',
            'invoice_type', 'handled_by', 'our_ref', 'delivery_no', 'your_ref',
            'supplier_name', 'supplier_address', 'supplier_tel', 'supplier_fax',
            'supplier_email', 'customer_name', 'customer_address', 'goods_value',
            'vat_code', 'vat_rate_percent', 'vat_amount', 'total_amount', 'batch',
            'expiry_date'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ""
                
        # Reorder columns to match expected output format
        df = df[expected_columns]
        
        return df
        
    except Exception as e:
        logger.error(f"Error extracting invoice data: {e}")
        return None

def main():
    """Main function to run from command line."""
    if len(sys.argv) < 2:
        print("Usage: python extract_invoice_data.py <input_file> [output_file]")
        return 1
        
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "invoice_data.xlsx"
    
    try:
        # Read invoice text from file
        with open(input_file, 'r') as f:
            invoice_text = f.read()
            
        # Extract data using GPT-4o
        df = extract_invoice_data(invoice_text)
        if df is None:
            return 1
            
        # Save to Excel
        df.to_excel(output_file, index=False)
        print(f"Successfully extracted invoice data to {output_file}")
        
        # Also print as formatted text table
        print("\nExtracted Data:")
        print(df.to_string())
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
