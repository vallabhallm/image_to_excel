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

def process_fehilys_directory(directory_path):
    """Special function to process Feehily's invoices.
    
    Args:
        directory_path: Path to directory containing Feehily's invoices
        
    Returns:
        DataFrame with extracted data
    """
    logger.info(f"Using special processing for Feehily's directory: {directory_path}")
    
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
    
    # Find all PDF files manually
    files = []
    try:
        for file in os.listdir(directory_path):
            if file.endswith('.pdf'):
                files.append(os.path.join(directory_path, file))
        logger.info(f"Found {len(files)} PDF files in Feehily's directory")
    except Exception as e:
        logger.error(f"Error listing files in directory: {e}")
        return None
    
    # Process each file individually
    results = []
    for file_path in files:
        logger.info(f"Processing Feehily's file: {file_path}")
        df = parser.process_file(file_path)
        if df is not None and not df.empty:
            file_name = os.path.basename(file_path)
            df['source_file'] = file_name
            results.append(df)
    
    # Combine results
    if results:
        combined_df = pd.concat(results, ignore_index=True)
        logger.info(f"Successfully processed {len(results)} Feehily's files with {len(combined_df)} rows")
        return combined_df
    else:
        logger.warning("No valid data extracted from Feehily's files")
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
    
    # Store Feehily's directory processing status
    feehilys_processed = False
    
    # Process each subdirectory
    all_data = {}
    
    # Hard-code special processing for Feehily's directory first
    for subdir in subdirs:
        if "Feehily" in subdir or "feehily" in subdir or "Fehily" in subdir:
            logger.info(f"MATCH FOUND: Detected Feehily's directory: '{subdir}'")
            subdir_path = os.path.join(base_dir, subdir)
            
            # Process Feehily's directory directly
            feehilys_processed = True
            
            # List files in the directory
            try:
                files = [f for f in os.listdir(subdir_path) if f.endswith('.pdf')]
                logger.info(f"Found {len(files)} PDF files in Feehily's directory: {files}")
                
                # Process each file individually
                config = ConfigManager()
                api_key = config.get('openai', 'api_key')
                parser = GPTInvoiceParser(api_key)
                
                results = []
                for file_name in files:
                    file_path = os.path.join(subdir_path, file_name)
                    logger.info(f"Processing Feehily's file: {file_path}")
                    df = parser.process_file(file_path)
                    if df is not None and not df.empty:
                        df['source_file'] = file_name
                        results.append(df)
                
                if results:
                    combined_df = pd.concat(results, ignore_index=True)
                    logger.info(f"Successfully processed {len(results)} Feehily's files with {len(combined_df)} rows")
                    all_data["3 Feehilys invoices"] = combined_df
                    logger.info(f"Added {len(combined_df)} rows from {subdir} using direct processing")
                    
            except Exception as e:
                logger.error(f"Error processing Feehily's directory: {e}")
    
    # Then process the remaining directories
    for subdir in subdirs:
        # Skip Feehily's directory if we already processed it
        if "Feehily" in subdir or "feehily" in subdir or "Fehily" in subdir:
            if feehilys_processed:
                logger.info(f"Skipping Feehily's directory '{subdir}' as it was already processed")
                continue
        
        # More detailed debugging about each directory
        logger.info(f"\nProcessing directory: {subdir}")
        logger.info(f"Directory name check: '{subdir}' (representation: {repr(subdir)})")
        
        subdir_path = os.path.join(base_dir, subdir)
        
        # Debug - Show files in directory
        try:
            files = os.listdir(subdir_path)
            logger.info(f"Files in directory: {files}")
        except Exception as e:
            logger.error(f"Error listing files in {subdir_path}: {e}")
            continue  # Skip to the next directory if there's an error
        
        try:
            # Process the directory using our wrapper function
            cleaned_name = subdir.replace(' ', '_').replace("'", "")
            temp_filename = f"temp_{cleaned_name}.xlsx"
            results = process_directory(subdir_path, temp_filename)
            
            # Debug - Show results
            result_count = len(results) if results else 0
            logger.info(f"Results for {subdir}: {type(results)} with {result_count} items")
            
            # Add to our combined data if successful
            if results and isinstance(results, dict) and len(results) > 0:
                sheet_name = subdir.replace("'", "")  # Remove apostrophes from sheet names
                # Ensure the sheet name is Excel-friendly (31 chars max)
                if len(sheet_name) > 31:
                    sheet_name = sheet_name[:28] + "..."
                
                # Get the data from the first key in results
                first_key = next(iter(results))
                all_data[sheet_name] = results[first_key]
                logger.info(f"Added {len(all_data[sheet_name])} rows from {subdir}")
            else:
                logger.warning(f"No data processed from {subdir}")
        except Exception as e:
            logger.error(f"Error processing directory {subdir_path}: {e}")
    
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
