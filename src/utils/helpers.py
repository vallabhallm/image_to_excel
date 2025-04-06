"""Helper functions for the image to excel converter."""
from pathlib import Path
from PIL import Image
import io
from loguru import logger

def is_valid_file_type(file_path: str) -> bool:
    """Check if the file type is supported."""
    file_path = str(file_path).lower()
    return file_path.endswith(('.jpg', '.jpeg', '.png', '.pdf'))

def get_file_type(file_path: str) -> str:
    """Get the type of file (image, pdf, or unknown)."""
    file_path = str(file_path).lower()
    if file_path.endswith(('.jpg', '.jpeg', '.png')):
        return "image"
    elif file_path.endswith('.pdf'):
        return "pdf"
    return "unknown"

def load_image(image_path: str) -> Image.Image:
    """Load an image from a file path."""
    try:
        with open(image_path, 'rb') as f:
            img = Image.open(io.BytesIO(f.read()))
            return convert_to_rgb(img)
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None

def convert_to_rgb(img: Image.Image) -> Image.Image:
    """Convert an image to RGB mode if it isn't already."""
    if img.mode == 'RGB':
        return img
    return img.convert('RGB')

def save_image(img: Image.Image, output_path: str) -> bool:
    """Save an image to a file."""
    try:
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Error saving image to {output_path}: {e}")
        return False

def format_data(data):
    """Format extracted data for Excel output.
    
    Args:
        data: List of dictionaries containing extracted content
        
    Returns:
        List of formatted strings
    """
    if not data:
        return []
        
    formatted_data = []
    for item in data:
        if isinstance(item, dict) and "content" in item and item["content"]:
            formatted_data.append(item["content"])
    return formatted_data