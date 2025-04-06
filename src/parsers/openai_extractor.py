"""OpenAI extractor module."""
import os
import base64
import json
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
                            "text": "Extract all text from this invoice. Return only the extracted text without any additional formatting or explanation."
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

    def extract_structured_data(self, text: str) -> dict:
        """Extract structured data from invoice text.
        
        Args:
            text: Raw text extracted from invoice
            
        Returns:
            Dictionary with structured invoice data
        """
        if not text:
            logger.error("Empty text provided for structured extraction")
            return None
        
        try:
            # Create message to extract structured data
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a precise invoice data extraction assistant. Your task is to extract structured data from invoice text. "
                        "Format your response as valid JSON with the following structure:\n"
                        "{\n"
                        "  \"invoice_number\": \"string\",\n"
                        "  \"invoice_date\": \"YYYY-MM-DD\",\n"
                        "  \"vendor\": \"string\",\n"
                        "  \"customer\": \"string\",\n"
                        "  \"total_amount\": number,\n"
                        "  \"currency\": \"string\",\n"
                        "  \"payment_terms\": \"string\",\n"
                        "  \"items\": [\n"
                        "    {\n"
                        "      \"description\": \"string\",\n"
                        "      \"quantity\": number,\n"
                        "      \"unit_price\": number,\n"
                        "      \"amount\": number\n"
                        "    }\n"
                        "  ]\n"
                        "}\n"
                        "If you can't find a specific field, use null for its value. Extract as many line items as possible."
                    )
                },
                {
                    "role": "user",
                    "content": f"Extract structured data from this invoice text:\n\n{text}"
                }
            ]
            
            # Get model settings from config
            model = self.config.get('openai', 'chat', 'model') or "gpt-4"
            max_tokens = self.config.get('openai', 'chat', 'max_tokens') or 2000
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1  # Low temperature for more deterministic outputs
            )
            
            # Extract and parse JSON from response
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                # Extract JSON if enclosed in ``` blocks
                if "```json" in content and "```" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                    
                # Parse JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON from response: {e}")
                    logger.debug(f"Response content: {content}")
                    return {"raw_text": text}
                    
            logger.error("No data found in API response")
            return {"raw_text": text}
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {"raw_text": text}

    def extract_data(self, content: bytes) -> dict:
        """Extract structured data from content.
        
        Args:
            content: Content to extract data from
            
        Returns:
            Extracted structured data or raw text if structure extraction fails
        """
        # First extract the raw text
        text = self.extract_text(content)
        if not text:
            return None
            
        # Then extract structured data from the text
        structured_data = self.extract_structured_data(text)
        if not structured_data:
            return {"raw_text": text}
            
        return structured_data
