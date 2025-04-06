"""Main module."""
import os
import sys
from loguru import logger
from src.parsers.image_parser import ImageParser
from src.generators.excel_generator import ExcelGenerator
from src.utils.config_manager import ConfigManager

def main(args=None):
    """Main function.
    
    Args:
        args: Command line arguments
        
    Returns:
        0 on success, 1 on failure
    """
    if args is None:
        args = sys.argv[1:]
        
    if len(args) < 2:
        logger.error("Usage: python main.py <input_directory> <output_file>")
        sys.exit(1)
        
    input_dir = args[0]
    output_file = args[1]
    
    if not os.path.exists(input_dir):
        logger.error(f"Input directory not found: {input_dir}")
        sys.exit(1)
        
    try:
        # Get API key from config
        config = ConfigManager()
        api_key = config.get('openai', 'api_key')
        if not api_key:
            logger.error("OpenAI API key not found in configuration")
            sys.exit(1)
            
        parser = ImageParser(api_key)
        
        # Parse directory
        results = parser.parse_directory(input_dir)
        if not results:
            logger.error("No text extracted from files")
            sys.exit(1)
            
        # Generate Excel file
        generator = ExcelGenerator()
        if not generator.create_excel(results, output_file):
            logger.error("Failed to create Excel file")
            sys.exit(1)
            
        logger.info(f"Successfully created Excel file: {output_file}")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())