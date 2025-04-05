import os
import sys
import yaml
from typing import Dict
from loguru import logger
from src.parsers.image_parser import ImageParser
from src.generators.excel_generator import ExcelGenerator

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/image_to_excel_{time}.log",
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

def load_config(config_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf', 'api_config.yaml')) -> dict:
    """Load configuration from YAML file.

    Args:
        config_path (str, optional): Path to config file. Defaults to 'api_config.yaml'.

    Returns:
        dict: Configuration dictionary.
    """
    try:
        logger.debug(f"Loading configuration from {config_path}")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully")
            return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise Exception(f"Failed to load configuration: {str(e)}")

def main():
    """Main function to process images and generate Excel."""
    try:
        # Load configuration
        logger.info("Starting image to Excel conversion")
        config = load_config()
        
        # Check if input directory is provided
        if len(sys.argv) != 2:
            logger.error("Usage: python main.py <input_directory>")
            sys.exit(1)

        input_directory = sys.argv[1]
        
        # Check if input directory exists
        if not os.path.exists(input_directory):
            logger.error(f"Error: Directory '{input_directory}' not found")
            sys.exit(1)

        # Initialize parser and generator
        logger.debug("Initializing ImageParser and ExcelGenerator")
        parser = ImageParser(config['openai']['api_key'])
        generator = ExcelGenerator()

        # Process directory and extract data
        logger.info("Processing input directory")
        directory_responses = parser.parse_directory(input_directory)
        if not any(len(responses) > 0 for responses in directory_responses.values()):
            logger.error("No data was extracted from the images")
            sys.exit(1)

        # Create Excel file
        logger.info("Generating Excel file")
        generator.create_excel(directory_responses)

        # Save Excel file
        output_path = os.path.join(os.path.dirname(input_directory), 
                                 config['output']['excel']['default_filename'])
        if generator.save_excel(output_path):
            logger.info(f"Excel file saved successfully: {output_path}")
        else:
            logger.error("Error: Failed to save Excel file")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()