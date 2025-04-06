"""Generator interface module."""
from abc import ABC, abstractmethod

class GeneratorInterface(ABC):
    """Generator interface class."""

    @abstractmethod
    def create_excel(self, data: dict, output_path: str) -> bool:
        """Create Excel file from data.
        
        Args:
            data: Dictionary mapping sheet names to lists of dictionaries
            output_path: Path to save Excel file
            
        Returns:
            True if successful, False otherwise
        """
        pass
