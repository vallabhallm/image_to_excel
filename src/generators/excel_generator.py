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
                    
                    # Extract content from sheet data
                    content_list = []
                    for item in sheet_data:
                        if isinstance(item, dict) and "content" in item and item["content"]:
                            content_list.append({"Content": item["content"]})
                            
                    # Skip if no valid content
                    if not content_list:
                        continue
                        
                    # Create DataFrame and write to Excel
                    df = pd.DataFrame(content_list)
                    df.to_excel(writer, sheet_name=final_name, index=False)
                    
                # Check if any sheets were written
                if not used_sheet_names:
                    logger.error("No valid sheets to write")
                    return False
                    
            logger.info(f"Successfully created Excel file: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Excel file: {e}")
            return False