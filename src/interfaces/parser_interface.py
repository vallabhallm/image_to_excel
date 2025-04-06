"""Parser interface module."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from pathlib import Path

class FileParser(ABC):
    """Abstract base class for file parsers."""
    
    @abstractmethod
    def can_handle(self, file_path: Union[str, Path]) -> bool:
        """Check if this parser can handle the given file."""
        pass

    @abstractmethod
    def parse(self, file_path: Union[str, Path]) -> Optional[Dict]:
        """Parse the file and return extracted data."""
        pass

class DirectoryParser(ABC):
    """Abstract base class for directory parsers."""
    
    @abstractmethod
    def parse_directory(self, directory_path: Union[str, Path]) -> Dict[str, List[Dict]]:
        """Parse all files in a directory and its subdirectories."""
        pass

class DataExtractor(ABC):
    """Abstract base class for data extraction."""
    
    @abstractmethod
    def extract_data(self, content: Union[str, bytes]) -> Optional[Dict]:
        """Extract data from content."""
        pass

class ParserInterface(ABC):
    """Parser interface."""

    @abstractmethod
    def process_file(self, file_path: str) -> Optional[List[Dict]]:
        """Process a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of dictionaries containing extracted content
        """
        pass

    @abstractmethod
    def parse_directory(self, directory_path: str) -> Dict[str, List[Dict]]:
        """Parse all files in a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            Dictionary mapping filenames to extracted content
        """
        pass
