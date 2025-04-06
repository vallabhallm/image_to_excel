#!/usr/bin/env python
"""Demo script for supplier-specific invoice processing."""

import os
import sys
import pandas as pd
from loguru import logger
from src.parsers.gpt_invoice_parser import GPTInvoiceParser
from src.utils.supplier_detector import SupplierDetector


def process_invoices_by_supplier(input_dir, output_file):
    """Process all invoices using supplier-specific templates and combine results."""
    # Initialize the parser
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
        return 1
        
    parser = GPTInvoiceParser(api_key=api_key)
    
    # Find all supplier directories
    supplier_dirs = []
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path) and "invoice" in item.lower():
            supplier_dirs.append(item_path)
    
    if not supplier_dirs:
        print(f"No supplier directories found in {input_dir}")
        return 1
        
    print(f"Found {len(supplier_dirs)} supplier directories")
    
    # Process each supplier directory
    all_results = []
    
    for supplier_dir in supplier_dirs:
        supplier_name = os.path.basename(supplier_dir)
        print(f"\nProcessing {supplier_name}...")
        
        # Use the process_directory method from GPTInvoiceParser
        results = parser.process_directory(supplier_dir)
        
        if results:
            for key, df in results.items():
                print(f"  - Extracted {len(df)} line items from {key}")
                
                # Print sample of data
                if not df.empty:
                    print("\nSample data:")
                    sample_cols = ['qty', 'description', 'price', 'invoice_number', 'invoice_date', 'supplier_type']
                    display_cols = [col for col in sample_cols if col in df.columns]
                    print(df[display_cols].head(2).to_string())
                    print("\n")
                
                all_results.append(df)
        else:
            print(f"  - No results for {supplier_name}")
    
    if all_results:
        # Combine all results into a single DataFrame
        combined_df = pd.concat(all_results, ignore_index=True)
        
        # Save results
        combined_df.to_excel(output_file, index=False)
        combined_df.to_csv(output_file.replace('.xlsx', '.csv'), index=False)
        
        print(f"\nProcessed {len(combined_df)} invoice line items")
        print(f"Results saved to {output_file} and {output_file.replace('.xlsx', '.csv')}")
        
        # Create supplier-specific sheets as well
        with pd.ExcelWriter(output_file.replace('.xlsx', '_by_supplier.xlsx')) as writer:
            # First sheet is combined data
            combined_df.to_excel(writer, sheet_name='All Invoices', index=False)
            
            # Create a sheet for each supplier
            suppliers = combined_df['supplier_type'].unique()
            for supplier in suppliers:
                supplier_df = combined_df[combined_df['supplier_type'] == supplier]
                supplier_df.to_excel(writer, sheet_name=f'{supplier.title()}', index=False)
        
        print(f"Supplier-specific sheets saved to {output_file.replace('.xlsx', '_by_supplier.xlsx')}")
        
        return 0
    else:
        print("No invoice data extracted")
        return 1


if __name__ == "__main__":
    # Set up logging
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    # Get input and output paths
    if len(sys.argv) >= 3:
        input_dir = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_dir = "data/INVOICES FOR WELLSTONE DRUGS PURCHASES (2024)"
        output_file = "output/supplier_specific_results.xlsx"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"Processing invoices from: {input_dir}")
    print(f"Output will be saved to: {output_file}")
    
    try:
        sys.exit(process_invoices_by_supplier(input_dir, output_file))
    except Exception as e:
        print(f"Error processing invoices: {e}")
        sys.exit(1)
