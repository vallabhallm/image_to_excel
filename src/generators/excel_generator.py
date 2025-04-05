import os
import re
from typing import Dict, List, Union
import pandas as pd
from loguru import logger

class ExcelGenerator:
    """Class to generate Excel files from extracted data."""

    def __init__(self):
        """Initialize the ExcelGenerator."""
        logger.debug("Initializing ExcelGenerator")
        self.data = {}

    def clean_sheet_name(self, name: str) -> str:
        """Clean sheet name to be valid for Excel.

        Args:
            name (str): Sheet name to clean.

        Returns:
            str: Cleaned sheet name.
        """
        if not name:
            logger.warning("Empty sheet name provided, using 'Sheet1'")
            return "Sheet1"
        
        # Replace invalid characters with underscore
        cleaned = re.sub(r'[\[\]:*?/\\]', '_', name)
        # Remove multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        # Truncate to 31 characters (Excel limit)
        cleaned = cleaned[:31]
        # Handle empty result
        if not cleaned:
            cleaned = "Sheet1"
        
        logger.debug(f"Cleaned sheet name: {name} -> {cleaned}")
        return cleaned

    def create_excel(self, data: Dict[str, List[Dict]]) -> None:
        """
        Create Excel sheets from the provided data.

        Args:
            data (Dict[str, List[Dict]]): A dictionary where keys are sheet names and values are
                                         lists of dictionaries containing the data for each sheet.
        """
        logger.info("Creating Excel workbook")
        try:
            self.data = {}
            # Create a DataFrame for each directory/sheet
            for sheet_name, responses in data.items():
                # Convert the list of dictionaries to a DataFrame
                df = pd.DataFrame(responses)
                # Clean sheet name (Excel has restrictions on sheet names)
                clean_sheet_name = self.clean_sheet_name(sheet_name)
                self.data[clean_sheet_name] = df
                logger.debug(f"Created sheet: {clean_sheet_name}")

        except Exception as e:
            logger.error(f"Error creating Excel workbook: {str(e)}")
            raise

    def save_excel(self, output_path: str) -> bool:
        """
        Save the Excel file to the specified path.

        Args:
            output_path (str): Path where the Excel file should be saved.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.data:
            logger.error("No data to save")
            return False

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the workbook
            logger.info(f"Saving Excel file to: {output_path}")
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in self.data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            logger.info(f"Excel file saved successfully to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving Excel file: {str(e)}")
            return False