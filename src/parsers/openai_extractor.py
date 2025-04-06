"""OpenAI extractor module."""
import os
import base64
import openai
from loguru import logger
from src.interfaces.parser_interface import DataExtractor
from src.utils.config_manager import ConfigManager

class OpenAIExtractor(DataExtractor):
    """OpenAI extractor class."""

    def __init__(self, api_key: str = None):
        """Initialize the OpenAI extractor.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("OpenAI API key not provided")
            
        self.client = openai.OpenAI(api_key=self.api_key)
        self.config = ConfigManager()

    def extract_text(self, image_bytes: bytes) -> str:
        """Extract text from image using OpenAI's Vision API.
        
        Args:
            image_bytes: Image bytes
            
        Returns:
            Extracted text or None if extraction failed
        """
        if not image_bytes:
            logger.error("Empty image bytes provided")
            return None
            
        try:
            # Encode image bytes to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Create message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Return only the extracted text without any additional formatting or explanation."
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
            
            # Get model settings from config
            model = self.config.get('openai', 'vision', 'model')
            max_tokens = self.config.get('openai', 'vision', 'max_tokens')
            
            if not model:
                logger.error("OpenAI model not found in configuration")
                return None
            
            # Call OpenAI API with configured model
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens or 1000  # Use config value or default to 1000
            )
            
            # Extract text from response
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
                
            logger.error("No text found in API response")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return None

    def extract_data(self, content: bytes) -> str:
        """Extract data from content.
        
        Args:
            content: Content to extract data from
            
        Returns:
            Extracted data
        """
        return self.extract_text(content)
