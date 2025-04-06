"""Image parser module."""
import os
import io
import fitz
from PIL import Image, ImageEnhance
from loguru import logger
from .openai_extractor import OpenAIExtractor
from ..utils.config_manager import ConfigManager

class ImageParser:
    """Image parser class."""
    
    def __init__(self, api_key: str = None):
        """Initialize parser.
        
        Args:
            api_key: OpenAI API key
        """
        logger.debug("Initializing ImageParser")
        if not api_key:
            config = ConfigManager()
            api_key = config.get('openai', 'api_key')
            if not api_key:
                raise ValueError("OpenAI API key not found in config")
        self.extractor = OpenAIExtractor(api_key)
        
    def is_image_file(self, file_path: str) -> bool:
        """Check if file is an image.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is an image, False otherwise
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                logger.debug(f"File {file_path} is not supported (extension: {ext})")
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking file type: {e}")
            return False
            
    def is_pdf_file(self, file_path: str) -> bool:
        """Check if file is a PDF.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is a PDF, False otherwise
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext != '.pdf':
                logger.debug(f"File {file_path} is not a PDF (extension: {ext})")
                return False
            logger.debug(f"File {file_path} is a PDF")
            return True
        except Exception as e:
            logger.error(f"Error checking file type: {e}")
            return False
            
    def process_image(self, image_path: str) -> dict:
        """Process an image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing extracted text
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None
            
        if not self.is_image_file(image_path):
            logger.error(f"Invalid image file: {image_path}")
            return None
            
        try:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
                text = self.extractor.extract_text(image_bytes)
                if text:
                    return {"content": text}
                logger.error("Failed to extract text from image")
                return None
                    
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
            
    def process_pdf(self, pdf_path: str) -> list:
        """Process a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries containing extracted text
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
            
        if not self.is_pdf_file(pdf_path):
            logger.error(f"Invalid PDF file: {pdf_path}")
            return None
            
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                logger.error("PDF has no pages")
                return None
                
            results = []
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    # Increase resolution and use RGB color space
                    zoom = 2.0  # Increase zoom for better quality
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                    
                    # Convert pixmap to PIL Image
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    
                    # Enhance image quality
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.5)  # Increase contrast
                    
                    # Convert PIL Image to bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG', quality=95)  # Increase quality
                    img_byte_arr.seek(0)
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Extract text
                    text = self.extractor.extract_text(img_byte_arr)
                    if text:
                        results.append({"content": text})
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num}: {e}")
                    continue
                    
            if not results:
                logger.error("No text extracted from any page")
                return None
                
            return results
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return None
            
    def process_file(self, file_path: str) -> list:
        """Process a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of dictionaries containing extracted text
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        try:
            if self.is_image_file(file_path):
                result = self.process_image(file_path)
                return [result] if result else None
                
            elif self.is_pdf_file(file_path):
                return self.process_pdf(file_path)
                
            else:
                logger.error(f"Unsupported file type: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return None
            
    def parse_directory(self, directory_path: str) -> dict:
        """Parse all files in a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            Dictionary mapping directory names to lists of extracted text
        """
        if not os.path.exists(directory_path):
            raise Exception(f"Directory not found: {directory_path}")
        if not os.path.isdir(directory_path):
            raise Exception(f"Not a directory: {directory_path}")
            
        results = {}
        for root, _, files in os.walk(directory_path):
            dir_results = []
            for file in files:
                file_path = os.path.join(root, file)
                if self.is_image_file(file_path):
                    result = self.process_image(file_path)
                    if result:
                        dir_results.append(result)
                elif self.is_pdf_file(file_path):
                    result = self.process_pdf(file_path)
                    if result:
                        dir_results.extend(result)
                        
            if dir_results:
                dir_name = os.path.basename(root)
                results[dir_name] = dir_results
                
        return results