"""Excel generator module."""
import os
import re
import pandas as pd
from loguru import logger
from src.interfaces.generator_interface import GeneratorInterface

class ExcelGenerator(GeneratorInterface):
    """Excel generator class."""

    def __init__(self):
        """Initialize the generator."""
        logger.debug("Initializing ExcelGenerator")

    def clean_sheet_name(self, sheet_name: str) -> str:
        """Clean sheet name for Excel compatibility.
        
        Args:
            sheet_name: Sheet name to clean
            
        Returns:
            Cleaned sheet name
        """
        if not sheet_name:
            return "Sheet1"
            
        # Remove invalid characters
        cleaned = re.sub(r'[\[\]:*?/\\]', '', sheet_name)
        
        # Truncate if too long (Excel limit is 31 chars)
        if len(cleaned) > 31:
            cleaned = cleaned[:31]
            
        # If empty after cleaning, use default
        if not cleaned:
            cleaned = "Sheet1"
            
        return cleaned

    def create_excel(self, data: dict, output_path: str) -> bool:
        """Create Excel file from data.
        
        Args:
            data: Dictionary mapping sheet names to lists of dictionaries
            output_path: Path to save Excel file
            
        Returns:
            True if successful, False otherwise
        """
        if not data:
            logger.error("No data provided")
            return False
            
        try:
            # Create parent directories if they don't exist
            dirname = os.path.dirname(output_path)
            if dirname:  # Only create directories if there's a directory path
                os.makedirs(dirname, exist_ok=True)
            
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                used_sheet_names = set()
                
                for sheet_name, sheet_data in data.items():
                    # Skip empty sheets
                    if not sheet_data:
                        continue
                        
                    # Clean sheet name
                    clean_name = self.clean_sheet_name(sheet_name)
                    
                    # Handle duplicate sheet names
                    counter = 1
                    final_name = clean_name
                    while final_name in used_sheet_names:
                        final_name = f"{clean_name}_{counter}"
                        counter += 1
                    used_sheet_names.add(final_name)
                    
                    # Process invoices - create a summary sheet and a details sheet
                    summary_data = []
                    line_items_data = []
                    
                    for index, item in enumerate(sheet_data):
                        if isinstance(item, dict):
                            # Handle raw text content (unstructured data)
                            if "raw_text" in item and item["raw_text"]:
                                summary_data.append({
                                    "Invoice ID": f"Unknown-{index}",
                                    "Date": None,
                                    "Vendor": "Unknown",
                                    "Customer": "Unknown",
                                    "Total Amount": None,
                                    "Currency": None,
                                    "Payment Terms": None,
                                    "Raw Text": item["raw_text"]
                                })
                            # Handle structured invoice data
                            elif "invoice_number" in item or "content" in item:
                                # Handle content from previous formatting
                                if "content" in item and isinstance(item["content"], str):
                                    summary_data.append({
                                        "Invoice ID": f"Unknown-{index}",
                                        "Date": None,
                                        "Vendor": "Unknown",
                                        "Customer": "Unknown",
                                        "Total Amount": None,
                                        "Currency": None,
                                        "Payment Terms": None,
                                        "Raw Text": item["content"]
                                    })
                                else:
                                    # Process structured invoice data
                                    invoice_number = item.get("invoice_number", f"Unknown-{index}")
                                    invoice_date = item.get("invoice_date")
                                    vendor = item.get("vendor", "Unknown")
                                    customer = item.get("customer", "Unknown")
                                    total_amount = item.get("total_amount")
                                    currency = item.get("currency", "")
                                    payment_terms = item.get("payment_terms")
                                    
                                    summary_data.append({
                                        "Invoice ID": invoice_number,
                                        "Date": invoice_date,
                                        "Vendor": vendor,
                                        "Customer": customer,
                                        "Total Amount": total_amount,
                                        "Currency": currency,
                                        "Payment Terms": payment_terms
                                    })
                                    
                                    # Process line items if available
                                    items = item.get("items", [])
                                    for line_item in items:
                                        if isinstance(line_item, dict):
                                            line_items_data.append({
                                                "Invoice ID": invoice_number,
                                                "Description": line_item.get("description", ""),
                                                "Quantity": line_item.get("quantity"),
                                                "Unit Price": line_item.get("unit_price"),
                                                "Amount": line_item.get("amount")
                                            })
                    
                    # Create summary sheet                    
                    if summary_data:
                        df_summary = pd.DataFrame(summary_data)
                        df_summary.to_excel(writer, sheet_name=final_name, index=False)
                        
                        # Create line items sheet if there are line items
                        if line_items_data:
                            line_items_sheet_name = f"{final_name}_Items"
                            counter = 1
                            while line_items_sheet_name in used_sheet_names:
                                line_items_sheet_name = f"{final_name}_Items_{counter}"
                                counter += 1
                            used_sheet_names.add(line_items_sheet_name)
                            
                            df_items = pd.DataFrame(line_items_data)
                            df_items.to_excel(writer, sheet_name=line_items_sheet_name, index=False)
                    
                # Check if any sheets were written
                if not used_sheet_names:
                    logger.error("No valid sheets to write")
                    return False
                    
            logger.info(f"Successfully created Excel file: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Excel file: {e}")
            return False