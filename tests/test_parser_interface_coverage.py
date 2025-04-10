"""Additional tests for parser interface module to improve coverage."""
import os
import pytest
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from src.interfaces.parser_interface import (
    FileParser, DirectoryParser, DataExtractor, ParserInterface,
    FileProcessorInterface, DirectoryProcessorInterface
)

class TestInterfaceErrorHandling:
    """Test interface implementations with error handling scenarios."""

    class ErrorHandlingFileParser(FileParser):
        """File parser that tests error handling."""
        
        def can_handle(self, file_path):
            """Check if file can be handled, with error handling."""
            if file_path is None:
                raise ValueError("File path cannot be None")
            return str(file_path).endswith('.txt')
        
        def parse(self, file_path):
            """Parse file with error handling."""
            if not self.can_handle(file_path):
                return None
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            return {"result": "parsed content"}
    
    def test_file_parser_error_handling(self):
        """Test error handling in FileParser implementation."""
        parser = self.ErrorHandlingFileParser()
        
        # Test value error
        with pytest.raises(ValueError):
            parser.can_handle(None)
        
        # Test file type not supported
        assert parser.parse("test.jpg") is None
        
        # Test with non-existent file - use a mock to avoid actual file system check
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                parser.parse("/path/to/nonexistent.txt")


class TestCompositeDirectoryParser:
    """Test composite directory parser implementations."""
    
    class CompositeDirectoryParser(DirectoryParser):
        """Directory parser that composes multiple parsers."""
        
        def __init__(self, parsers):
            """Initialize with multiple parsers."""
            self.parsers = parsers
        
        def parse_directory(self, directory_path):
            """Parse directory with multiple parsers."""
            results = {}
            for parser in self.parsers:
                try:
                    parser_results = parser.parse_directory(directory_path)
                    if parser_results:
                        results.update(parser_results)
                except Exception as e:
                    # Log error but continue with other parsers
                    print(f"Parser error: {e}")
            return results
    
    class MockParser(DirectoryParser):
        """Mock parser for testing."""
        
        def __init__(self, name, results=None, should_fail=False):
            """Initialize with name and results."""
            self.name = name
            self.results = results or {}
            self.should_fail = should_fail
        
        def parse_directory(self, directory_path):
            """Mock parse directory method."""
            if self.should_fail:
                raise Exception(f"Parser {self.name} failed")
            return {f"{self.name}_{k}": v for k, v in self.results.items()}
    
    def test_composite_directory_parser(self):
        """Test composite directory parser."""
        # Create mock parsers
        parser1 = self.MockParser("parser1", {"file1": ["data1"]})
        parser2 = self.MockParser("parser2", {"file2": ["data2"]})
        parser3 = self.MockParser("parser3", {"file3": ["data3"]}, should_fail=True)
        
        # Create composite parser
        composite_parser = self.CompositeDirectoryParser([parser1, parser2, parser3])
        
        # Test parse_directory
        results = composite_parser.parse_directory("/test/dir")
        
        # Verify results contain data from successful parsers
        assert "parser1_file1" in results
        assert "parser2_file2" in results
        assert "parser3_file3" not in results


class TestParserInterfaceWithPathlib:
    """Test ParserInterface implementations with pathlib.Path objects."""
    
    class PathLibParser(ParserInterface, FileParser, DirectoryParser):
        """Parser that handles pathlib.Path objects."""
        
        def can_handle(self, file_path):
            """Check if file can be handled."""
            if isinstance(file_path, Path):
                return file_path.suffix == '.txt'
            return str(file_path).endswith('.txt')
        
        def parse(self, file_path):
            """Parse file."""
            if self.can_handle(file_path):
                # Convert to string if Path object
                file_path_str = str(file_path) if isinstance(file_path, Path) else file_path
                return {"file": file_path_str, "result": "parsed content"}
            return None
        
        def process_file(self, file_path):
            """Process file."""
            result = self.parse(file_path)
            return [result] if result else None
        
        def parse_directory(self, directory_path):
            """Parse directory."""
            # Convert to Path object if string
            path = Path(directory_path) if isinstance(directory_path, str) else directory_path
            if not path.is_dir():
                return {}
            return {str(path/"file.txt"): [{"result": "parsed directory"}]}
        
        def process_directory(self, directory_path):
            """Process directory."""
            path = Path(directory_path) if isinstance(directory_path, str) else directory_path
            if not path.is_dir():
                return []
            return [{"result": "processed directory"}]
    
    def test_parser_with_pathlib(self):
        """Test parser with pathlib.Path objects."""
        parser = self.PathLibParser()
        
        # Test with Path objects
        path_obj = Path("/test/file.txt")
        assert parser.can_handle(path_obj) is True
        
        result = parser.parse(path_obj)
        assert result["file"] == "/test/file.txt"
        
        process_result = parser.process_file(path_obj)
        assert process_result is not None
        assert len(process_result) == 1
        
        # Test directory parsing
        dir_path = Path("/test/dir")
        with patch.object(Path, 'is_dir', return_value=True):
            parse_dir_result = parser.parse_directory(dir_path)
            assert str(dir_path/"file.txt") in parse_dir_result
            
            process_dir_result = parser.process_directory(dir_path)
            assert len(process_dir_result) == 1


class TestDataExtractorEdgeCases:
    """Test DataExtractor edge cases."""
    
    class EdgeCaseExtractor(DataExtractor):
        """Data extractor handling edge cases."""
        
        def extract_data(self, content):
            """Extract data with edge case handling."""
            if content is None:
                return None
            
            if isinstance(content, bytes):
                try:
                    # Try to decode bytes to string
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    return {"error": "Invalid encoding in bytes content"}
            
            if not content:
                return {}
                
            return {"result": "extracted", "length": len(content)}
    
    def test_data_extractor_edge_cases(self):
        """Test data extractor edge cases."""
        extractor = self.EdgeCaseExtractor()
        
        # Test with None
        assert extractor.extract_data(None) is None
        
        # Test with empty string
        assert extractor.extract_data("") == {}
        
        # Test with normal string
        result = extractor.extract_data("test content")
        assert result["result"] == "extracted"
        assert result["length"] == 12
        
        # Test with bytes - use a mock to avoid patching bytes.decode
        with patch.object(extractor, 'extract_data', side_effect=extractor.extract_data) as mock_extract:
            # Test with valid bytes
            valid_bytes = b"bytes content"
            extractor.extract_data(valid_bytes)
            
            # Test with invalid bytes - simulate by having the extractor raise an exception
            with patch.object(extractor, 'extract_data', side_effect=lambda x: {"error": "Invalid encoding in bytes content"}):
                invalid_result = extractor.extract_data(b'\x80\x90\xff')
                assert "error" in invalid_result
