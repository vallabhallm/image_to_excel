#!/usr/bin/env python3
"""
Process all invoice files in all subdirectories and combine results.
"""
import os
import sys
import pandas as pd
from loguru import logger
from src.parsers.gpt_invoice_parser import GPTInvoiceParser
from src.generators.excel_generator import ExcelGenerator
from src.utils.config_manager import ConfigManager

def process_directory(directory_path, output_file):
    """Process a directory of invoice files.
    
    Args:
        directory_path: Path to directory containing invoice files
        output_file: Path to output Excel file
        
    Returns:
        Dictionary with sheet names as keys and pandas DataFrames as values
    """
    if not os.path.exists(directory_path):
        logger.error(f"Input directory not found: {directory_path}")
        return None
    
    # Get API key from config
    try:
        config = ConfigManager()
        api_key = config.get('openai', 'api_key')
        if not api_key:
            logger.error("OpenAI API key not found in configuration")
            return None
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return None
    
    # Initialize GPT invoice parser
    parser = GPTInvoiceParser(api_key)
    
    # Process all files in directory
    try:
        results = parser.process_directory(directory_path)
        return results
    except Exception as e:
        logger.error(f"Error processing directory: {e}")
        return None

def main():
    """Main function to process all subdirectories."""
    if len(sys.argv) < 2:
        print("Usage: python process_all_invoices.py <base_directory> [output_file]")
        sys.exit(1)
    
    base_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "all_invoices_combined.xlsx"
    
    if not os.path.exists(base_dir):
        logger.error(f"Base directory not found: {base_dir}")
        sys.exit(1)
    
    # Find all subdirectories
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    logger.info(f"Found {len(subdirs)} subdirectories: {subdirs}")
    
    # Process each subdirectory
    all_data = {}
    
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        logger.info(f"\nProcessing directory: {subdir_path}")
        
        # Process the directory using our wrapper function
        results = process_directory(subdir_path, f"temp_{subdir.replace(' ', '_')}.xlsx")
        
        # Add to our combined data if successful
        if results and isinstance(results, dict) and len(results) > 0:
            sheet_name = subdir
            # Ensure the sheet name is Excel-friendly (31 chars max)
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:28] + "..."
            
            # Get the data from the first key in results
            first_key = next(iter(results))
            all_data[sheet_name] = results[first_key]
            logger.info(f"Added {len(all_data[sheet_name])} rows from {subdir}")
    
    # Create the combined Excel file
    if all_data:
        generator = ExcelGenerator()
        success = generator.create_excel(all_data, output_file)
        if success:
            logger.info(f"\nSuccessfully created combined Excel file: {output_file}")
            
            # Also create a single sheet version with all data combined
            combined_df = pd.concat([df for df in all_data.values() if isinstance(df, pd.DataFrame)], 
                                    ignore_index=True)
            
            if not combined_df.empty:
                combined_file = f"{os.path.splitext(output_file)[0]}_single_sheet.xlsx"
                combined_data = {"All Invoices": combined_df}
                generator.create_excel(combined_data, combined_file)
                logger.info(f"Created single-sheet version: {combined_file}")
        else:
            logger.error("\nFailed to create combined Excel file")
    else:
        logger.warning("\nNo data was processed from any subdirectory")

if __name__ == "__main__":
    main()
