import os
import sys
import base64
import openai
import yaml
from typing import Dict, List, Optional
from pdf2image import convert_from_path
import io
import fitz  # PyMuPDF
from loguru import logger

class ImageParser:
    def __init__(self, api_key: str):
        """
        Initialize the ImageParser with OpenAI API key.

        Args:
            api_key (str): OpenAI API key
        """
        logger.debug("Initializing ImageParser")
        self.api_key = api_key
        openai.api_key = api_key
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """
        Load configuration from YAML file.

        Returns:
            Dict: Configuration dictionary
        """
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'conf', 'api_config.yaml')
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}")
            raise Exception(f"Failed to load configuration file: {e}")

    def is_image_file(self, file_path: str) -> bool:
        """
        Check if a file is an image or PDF based on its extension.

        Args:
            file_path (str): Path to the file to check.

        Returns:
            bool: True if the file is an image or PDF, False otherwise.
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.pdf'}
        _, ext = os.path.splitext(file_path.lower())
        logger.debug(f"File {file_path} is{' ' if ext in image_extensions else ' not '}supported (extension: {ext})")
        return ext in image_extensions

    def parse_image(self, image_path: str) -> Optional[Dict]:
        """
        Parse an image file.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Optional[Dict]: Parsed data from the image, or None if parsing fails.
        """
        return self.process_file(image_path)

    def extract_data(self) -> Optional[Dict]:
        """
        Extract data from an image. To be implemented by subclasses.

        Returns:
            Optional[Dict]: Extracted data, or None if extraction fails.
        """
        return None

    def process_file(self, file_path: str) -> Dict:
        """
        Process an image or PDF file and extract data.

        Args:
            file_path (str): Path to the file to process.

        Returns:
            Dict: Extracted data from the file. For PDFs, returns a list of results (one per page).
                 For images, returns a single result dictionary.
        """
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} does not exist")
            return None

        _, ext = os.path.splitext(file_path.lower())
        
        # Check if file is supported
        if not self.is_image_file(file_path):
            logger.error(f"Unsupported file type {ext}")
            return None

        # Handle PDF files
        if ext == '.pdf':
            logger.info(f"Processing PDF file: {file_path}")
            try:
                # Open the PDF file
                document = fitz.open(file_path)
                results = []
                
                # Handle empty PDF
                if len(document) == 0:
                    logger.warning(f"PDF file {file_path} is empty")
                    return []
                
                try:
                    for page_number in range(len(document)):
                        try:
                            # Render page to an image
                            logger.debug(f"Processing page {page_number + 1} of {len(document)}")
                            page = document.load_page(page_number)
                            pix = page.get_pixmap()
                            image_bytes = io.BytesIO(pix.tobytes())
                            result = self.process_image(image_bytes)
                            if result:
                                results.append(result)
                            else:
                                logger.warning(f"No data extracted from page {page_number + 1}")
                        except Exception as e:
                            logger.error(f"Error processing page {page_number + 1} of PDF {file_path}: {str(e)}")
                            continue
                    return results if results else None
                finally:
                    document.close()
                    logger.debug("PDF document closed")
            except Exception as e:
                logger.error(f"Error opening PDF file {file_path}: {str(e)}")
                return None
        
        # Handle image files (jpg, jpeg, png)
        elif ext in {'.jpg', '.jpeg', '.png'}:
            logger.info(f"Processing image file: {file_path}")
            try:
                result = self.process_image(file_path)
                return [result] if result else None
            except Exception as e:
                logger.error(f"Error processing image file {file_path}: {str(e)}")
                return None
        
        return None

    def process_image(self, image_path_or_bytes) -> Dict:
        """
        Process a single image and extract data.

        Args:
            image_path_or_bytes (str or BytesIO): Path to the image file or image bytes.

        Returns:
            Dict: Extracted data from the image.
        """
        try:
            if isinstance(image_path_or_bytes, str):
                if not self.is_image_file(image_path_or_bytes):
                    return None

                # Create a base64 encoded string of the image
                with open(image_path_or_bytes, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            else:
                base64_image = base64.b64encode(image_path_or_bytes.read()).decode('utf-8')

            # Create the messages for the API call
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract invoice details from this image."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            # Initialize OpenAI client
            client = openai.OpenAI(api_key=self.config['openai']['api_key'])

            # Call the OpenAI API
            response = client.chat.completions.create(
                model=self.config['openai']['vision']['model'],
                messages=messages,
                max_tokens=self.config['openai']['vision']['max_tokens']
            )

            # Extract and return the response content
            if not response or not response.choices:
                logger.warning("No response from OpenAI API")
                return None

            content = response.choices[0].message.content
            if not content:
                logger.warning("Empty content in API response")
                return None

            logger.info("Successfully extracted text from image")
            return {"content": content}

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return None

    def parse_directory(self, directory_path: str) -> Dict[str, List[Dict]]:
        """
        Parse all images in a directory and its subdirectories.

        Args:
            directory_path (str): Path to the directory to parse.

        Returns:
            Dict[str, List[Dict]]: Dictionary mapping directory names to lists of parsed data.
        """
        if not os.path.exists(directory_path):
            logger.error(f"Directory {directory_path} does not exist")
            raise Exception(f"Directory {directory_path} does not exist")

        logger.info(f"Parsing directory: {directory_path}")
        results = {}
        try:
            for root, _, files in os.walk(directory_path):
                logger.debug(f"Processing directory: {root}")
                dir_name = os.path.basename(root)
                results[dir_name] = []
                
                for file in files:
                    if self.is_image_file(file):
                        file_path = os.path.join(root, file)
                        logger.debug(f"Processing file: {file_path}")
                        result = self.process_file(file_path)
                        if result:
                            results[dir_name].append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error parsing directory {directory_path}: {e}")
            raise Exception(f"Error parsing directory {directory_path}: {e}")

def run_main():
    """
    Main function to run the image parser.
    """
    if len(sys.argv) != 3:
        logger.error("Usage: python image_parser.py <openai_api_key> <input_directory>")
        sys.exit(1)

    api_key = sys.argv[1]
    input_directory = sys.argv[2]

    parser = ImageParser(api_key)
    responses = parser.parse_directory(input_directory)
    logger.info("JSON Responses:")
    logger.info(responses)

if __name__ == "__main__":
    run_main()