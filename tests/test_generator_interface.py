"""Test generator interface module."""
import pytest
from unittest.mock import patch, Mock
from src.interfaces.generator_interface import GeneratorInterface
import re


class TestGeneratorInterface:
    """Test GeneratorInterface abstract base class implementations."""

    class ConcreteGenerator(GeneratorInterface):
        """Concrete implementation of GeneratorInterface for testing."""
        
        def create_excel(self, data, output_path):
            """Create Excel file from data."""
            if not data:
                return False
            if output_path == "error.xlsx":
                return False
            return True
    
    def test_generator_interface_subclass(self):
        """Test a concrete implementation of GeneratorInterface."""
        generator = self.ConcreteGenerator()
        
        # Test create_excel method with valid data and path
        data = {"Sheet1": [{"col1": "value1"}]}
        assert generator.create_excel(data, "test.xlsx") is True
        
        # Test create_excel method with empty data
        empty_data = {}
        assert generator.create_excel(empty_data, "test.xlsx") is False
        
        # Test create_excel method with error path
        assert generator.create_excel(data, "error.xlsx") is False


def test_generator_interface_abstract():
    """Test that GeneratorInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        GeneratorInterface()


# Integration test with another implementation
class TestExcelGeneratorInterface:
    """Test a more realistic Excel generator implementation."""
    
    class ExcelGeneratorWithLogging(GeneratorInterface):
        """Excel generator with logging capabilities."""
        
        def __init__(self):
            """Initialize generator with a log of operations."""
            self.log = []
        
        def create_excel(self, data, output_path):
            """Create Excel file with logging."""
            try:
                # Log the operation
                self.log.append(f"Creating Excel file at {output_path} with {len(data)} sheets")
                
                # Simulate Excel creation
                if not data:
                    self.log.append("Error: No data provided")
                    return False
                
                for sheet_name, sheet_data in data.items():
                    if not sheet_data:
                        self.log.append(f"Warning: Sheet {sheet_name} is empty")
                
                self.log.append("Excel file created successfully")
                return True
            except Exception as e:
                self.log.append(f"Error creating Excel file: {str(e)}")
                return False
    
    def test_excel_generator_with_logging(self):
        """Test Excel generator with logging."""
        generator = self.ExcelGeneratorWithLogging()
        
        # Test successful Excel creation
        data = {
            "Sheet1": [{"col1": "value1"}],
            "Sheet2": [{"col1": "value1"}, {"col1": "value2"}]
        }
        result = generator.create_excel(data, "test.xlsx")
        
        assert result is True
        assert len(generator.log) > 0
        assert "Creating Excel file" in generator.log[0]
        assert "Excel file created successfully" in generator.log[-1]
        
        # Test empty data
        generator.log = []  # Reset log
        empty_result = generator.create_excel({}, "empty.xlsx")
        
        assert empty_result is False
        assert any("No data provided" in entry for entry in generator.log)
        
        # Test with error simulation
        generator.log = []  # Reset log
        
        # Create a new instance to avoid patching the method we're testing
        error_generator = self.ExcelGeneratorWithLogging()
        
        # Add a method that will trigger an exception
        def trigger_error(*args, **kwargs):
            error_generator.log.append("Error creating Excel file: Test error")
            raise Exception("Test error")
            
        # Replace the original method temporarily
        original_method = error_generator.create_excel
        error_generator.create_excel = trigger_error
        
        try:
            error_generator.create_excel(data, "error.xlsx")
        except Exception:
            pass  # Exception will be raised but we don't need to handle it
        
        # The log should contain the error
        assert any("Test error" in entry for entry in error_generator.log)


# Test for edge case handling
class TestGeneratorEdgeCases:
    """Test edge cases of GeneratorInterface implementations."""
    
    class EdgeCaseGenerator(GeneratorInterface):
        """Generator implementation focusing on edge cases."""
        
        def create_excel(self, data, output_path):
            """Handle edge cases in Excel creation."""
            # Handle None data
            if data is None:
                return False
                
            # Handle non-dict data
            if not isinstance(data, dict):
                return False
                
            # Handle invalid output path
            if not output_path or not isinstance(output_path, str):
                return False
                
            # Handle exotic sheet names
            for sheet_name in data.keys():
                # Excel has a 31 character limit for sheet names
                if len(str(sheet_name)) > 31:
                    return False
                    
                # Excel doesn't allow certain characters in sheet names
                if any(c in str(sheet_name) for c in r'[]*?:/\\'):
                    return False
            
            return True
    
    def test_generator_edge_cases(self):
        """Test edge case handling in generator."""
        generator = self.EdgeCaseGenerator()
        
        # Test None data
        assert generator.create_excel(None, "test.xlsx") is False
        
        # Test non-dict data
        assert generator.create_excel(["list", "not", "dict"], "test.xlsx") is False
        
        # Test invalid output path
        assert generator.create_excel({}, None) is False
        assert generator.create_excel({}, 123) is False
        
        # Test valid data with valid path
        valid_data = {"Sheet1": [{"col1": "value1"}]}
        assert generator.create_excel(valid_data, "test.xlsx") is True
        
        # Test data with long sheet name
        long_sheet_name = {"A" * 32: [{"col1": "value1"}]}
        assert generator.create_excel(long_sheet_name, "test.xlsx") is False
        
        # Test data with invalid sheet name characters
        invalid_sheet_name = {"Sheet*1": [{"col1": "value1"}]}
        assert generator.create_excel(invalid_sheet_name, "test.xlsx") is False


class TestGeneratorInterfaceEdgeCases:
    """Test edge cases for GeneratorInterface."""
    
    class EdgeCaseGenerator(GeneratorInterface):
        """Generator that handles various edge cases."""
        
        def __init__(self):
            """Initialize with error tracking."""
            self.errors = []
        
        def create_excel(self, data, output_path):
            """Create Excel file with extensive validation and error handling."""
            # Validate data input
            if data is None:
                self.errors.append("Null data received")
                return False
                
            if not isinstance(data, dict):
                self.errors.append(f"Invalid data type: {type(data)}")
                return False
                
            if not data:
                self.errors.append("Empty data dictionary")
                return False
                
            # Validate output path
            if output_path is None:
                self.errors.append("Null output path")
                return False
                
            if not isinstance(output_path, str):
                self.errors.append(f"Invalid output path type: {type(output_path)}")
                return False
                
            if not output_path:
                self.errors.append("Empty output path")
                return False
                
            # Check for illegal characters in path (basic simulation)
            illegal_chars = ['*', '?', '<', '>', '|', '"', ':']
            if any(char in output_path for char in illegal_chars):
                self.errors.append(f"Output path contains illegal characters: {output_path}")
                return False
                
            # Simulate directory not existing
            if not output_path.endswith('.xlsx') and not output_path.endswith('.xls'):
                self.errors.append("Output path must end with .xlsx or .xls")
                return False
                
            # Simulate success only for specific paths
            if "error" in output_path:
                self.errors.append("Simulated error in file creation")
                return False
                
            # Success case
            return True
    
    def test_generator_edge_cases(self):
        """Test generator with edge cases."""
        generator = self.EdgeCaseGenerator()
        
        # Test with None data
        assert not generator.create_excel(None, "output.xlsx")
        assert "Null data received" in generator.errors
        
        # Test with wrong data type
        assert not generator.create_excel("string data", "output.xlsx") 
        assert any("Invalid data type" in error for error in generator.errors)
        
        # Test with empty data
        assert not generator.create_excel({}, "output.xlsx")
        assert "Empty data dictionary" in generator.errors
        
        # Test with None output path
        assert not generator.create_excel({"data": "value"}, None)
        assert "Null output path" in generator.errors
        
        # Test with wrong output path type
        assert not generator.create_excel({"data": "value"}, 123)
        assert any("Invalid output path type" in error for error in generator.errors)
        
        # Test with empty output path
        assert not generator.create_excel({"data": "value"}, "")
        assert "Empty output path" in generator.errors
        
        # Test with illegal characters
        assert not generator.create_excel({"data": "value"}, "output*.xlsx")
        assert any("Output path contains illegal characters" in error for error in generator.errors)
        
        # Test with incorrect extension
        assert not generator.create_excel({"data": "value"}, "output.txt")
        assert any("Output path must end with .xlsx or .xls" in error for error in generator.errors)
        
        # Test simulated error
        assert not generator.create_excel({"data": "value"}, "error.xlsx")
        assert "Simulated error in file creation" in generator.errors
        
        # Test successful case
        assert generator.create_excel({"data": "value"}, "valid.xlsx")


class TestComplexDataHandling:
    """Test generator interface with complex data structures."""
    
    class ComplexDataGenerator(GeneratorInterface):
        """Generator that handles complex nested data structures."""
        
        def __init__(self):
            """Initialize tracking variables."""
            self.last_data = None
            self.last_output_path = None
            
        def create_excel(self, data, output_path):
            """Handle complex data structures and retain information about the call."""
            self.last_data = data
            self.last_output_path = output_path
            
            # Validate data structure contains required fields
            if not self._validate_data(data):
                return False
                
            # Success
            return True
            
        def _validate_data(self, data):
            """Validate data structure has required fields and format."""
            # Check for critical keys
            if not all(key in data for key in ['headers', 'rows']):
                return False
                
            # Check for proper array structures
            if not isinstance(data.get('headers'), list) or not isinstance(data.get('rows'), list):
                return False
                
            # Check for at least one header and matching column count in rows
            headers = data.get('headers', [])
            if not headers:
                return False
                
            # Verify row integrity
            for idx, row in enumerate(data.get('rows', [])):
                if not isinstance(row, list):
                    return False
                    
                if len(row) != len(headers):
                    # Row has different number of columns than headers
                    return False
                    
            # Data structure is valid
            return True
    
    def test_complex_data_structures(self):
        """Test with various complex data structures."""
        generator = self.ComplexDataGenerator()
        
        # Test with minimally valid data
        valid_data = {
            'headers': ['Name', 'Age', 'Email'],
            'rows': [
                ['John Doe', 30, 'john@example.com'],
                ['Jane Smith', 25, 'jane@example.com']
            ]
        }
        assert generator.create_excel(valid_data, "output.xlsx")
        
        # Test with missing required fields
        missing_headers = {
            'rows': [
                ['John Doe', 30, 'john@example.com']
            ]
        }
        assert not generator.create_excel(missing_headers, "output.xlsx")
        
        missing_rows = {
            'headers': ['Name', 'Age', 'Email']
        }
        assert not generator.create_excel(missing_rows, "output.xlsx")
        
        # Test with wrong data types
        wrong_header_type = {
            'headers': "Name,Age,Email",  # String instead of list
            'rows': [
                ['John Doe', 30, 'john@example.com']
            ]
        }
        assert not generator.create_excel(wrong_header_type, "output.xlsx")
        
        wrong_rows_type = {
            'headers': ['Name', 'Age', 'Email'],
            'rows': "John Doe,30,john@example.com\nJane Smith,25,jane@example.com"  # String instead of list
        }
        assert not generator.create_excel(wrong_rows_type, "output.xlsx")
        
        # Test with mismatched column counts
        mismatched_columns = {
            'headers': ['Name', 'Age', 'Email'],
            'rows': [
                ['John Doe', 30, 'john@example.com'],
                ['Jane Smith', 25]  # Missing email
            ]
        }
        assert not generator.create_excel(mismatched_columns, "output.xlsx")
        
        # Test with empty arrays
        empty_headers = {
            'headers': [],
            'rows': []
        }
        assert not generator.create_excel(empty_headers, "output.xlsx")
        
        # Test with nested data
        nested_data = {
            'headers': ['Name', 'Contact', 'Address'],
            'rows': [
                ['John Doe', {'email': 'john@example.com', 'phone': '555-1234'}, 
                 {'street': '123 Main St', 'city': 'Anytown', 'zip': '12345'}],
                ['Jane Smith', {'email': 'jane@example.com', 'phone': '555-5678'},
                 {'street': '456 Oak Ave', 'city': 'Somewhere', 'zip': '67890'}]
            ]
        }
        # This should work since we're just validating structure, not content types
        assert generator.create_excel(nested_data, "output.xlsx")
        assert generator.last_data == nested_data
        assert generator.last_output_path == "output.xlsx"


class TestGeneratorWithSheetOptions:
    """Test generator interface with sheet options."""
    
    class MultiSheetGenerator(GeneratorInterface):
        """Generator that supports multiple sheets and formatting options."""
        
        def create_excel(self, data, output_path):
            """Create Excel with support for multiple sheets and formatting."""
            # Validate basic requirements
            if not isinstance(data, dict):
                return False
                
            # Check for sheets configuration
            if 'sheets' not in data:
                # If no sheets specified, we need at least data for the default sheet
                if 'data' not in data:
                    return False
            else:
                # Validate sheets configuration
                sheets = data.get('sheets', [])
                if not isinstance(sheets, list) or not sheets:
                    return False
                    
                # Check each sheet has required data
                for sheet in sheets:
                    if not isinstance(sheet, dict) or 'name' not in sheet or 'data' not in sheet:
                        return False
                        
                    # Check sheet name is valid
                    if not isinstance(sheet['name'], str) or not sheet['name']:
                        return False
                        
                    # Sheet name length limit (31 chars for Excel)
                    if len(sheet['name']) > 31:
                        return False
            
            # Validate formatting options
            formatting = data.get('formatting', {})
            if formatting and not isinstance(formatting, dict):
                return False
                
            # Simulate successful creation
            return True
    
    def test_sheet_options(self):
        """Test with various sheet configurations."""
        generator = self.MultiSheetGenerator()
        
        # Test with single default sheet
        simple_data = {
            'data': [
                ['Header1', 'Header2'],
                ['Value1', 'Value2']
            ]
        }
        assert generator.create_excel(simple_data, "simple.xlsx")
        
        # Test with explicit single sheet
        single_sheet = {
            'sheets': [
                {
                    'name': 'Sheet1',
                    'data': [
                        ['Header1', 'Header2'],
                        ['Value1', 'Value2']
                    ]
                }
            ]
        }
        assert generator.create_excel(single_sheet, "single_sheet.xlsx")
        
        # Test with multiple sheets
        multi_sheet = {
            'sheets': [
                {
                    'name': 'Customers',
                    'data': [
                        ['Customer ID', 'Name', 'Email'],
                        ['C001', 'John Doe', 'john@example.com']
                    ]
                },
                {
                    'name': 'Orders',
                    'data': [
                        ['Order ID', 'Customer ID', 'Amount'],
                        ['O001', 'C001', 100.00]
                    ]
                }
            ]
        }
        assert generator.create_excel(multi_sheet, "multi_sheet.xlsx")
        
        # Test with formatting options
        formatted_data = {
            'sheets': [
                {
                    'name': 'Report',
                    'data': [
                        ['Category', 'Amount'],
                        ['Sales', 5000],
                        ['Expenses', 3000]
                    ]
                }
            ],
            'formatting': {
                'headers': {
                    'bold': True,
                    'bg_color': '#DDDDDD'
                },
                'columns': {
                    'Amount': {
                        'format': 'currency'
                    }
                }
            }
        }
        assert generator.create_excel(formatted_data, "formatted.xlsx")
        
        # Test with missing data
        missing_data = {
            'formatting': {
                'headers': {'bold': True}
            }
        }
        assert not generator.create_excel(missing_data, "missing_data.xlsx")
        
        # Test with invalid sheet config
        invalid_sheets = {
            'sheets': "Sheet1,Sheet2"  # String instead of list
        }
        assert not generator.create_excel(invalid_sheets, "invalid.xlsx")
        
        # Test with missing sheet name
        missing_name = {
            'sheets': [
                {
                    'data': [['A', 'B'], [1, 2]]
                }
            ]
        }
        assert not generator.create_excel(missing_name, "missing_name.xlsx")
        
        # Test with too long sheet name (Excel limit is 31 chars)
        long_name = {
            'sheets': [
                {
                    'name': 'This_is_an_extremely_long_sheet_name_that_exceeds_Excel_limits',
                    'data': [['A', 'B'], [1, 2]]
                }
            ]
        }
        assert not generator.create_excel(long_name, "long_name.xlsx")


class TestAdvancedIntegrationEdgeCases:
    """Test advanced edge cases in generator interface implementation."""
    
    class ComplexDataGenerator(GeneratorInterface):
        """Generator that handles more complex scenarios and configurations."""
        
        def create_excel(self, data, output_path):
            """Create Excel with complex validation and handling."""
            # Basic validation
            if not isinstance(data, dict) or not data:
                return False
                
            # Validate the output path has proper permissions (simulation)
            if output_path.startswith('/restricted/'):
                return False
                
            if output_path.startswith('/readonly/'):
                return False
                
            # Handle various data formats
            if 'raw_data' in data:
                # Process raw tabular data
                raw_data = data['raw_data']
                if not isinstance(raw_data, list):
                    return False
                    
                if not all(isinstance(row, list) for row in raw_data):
                    return False
            
            # Handle formulas
            if 'formulas' in data:
                formulas = data['formulas']
                if not isinstance(formulas, dict):
                    return False
                    
                for cell, formula in formulas.items():
                    if not isinstance(cell, str) or not isinstance(formula, str):
                        return False
                        
                    # Validate cell references (basic check)
                    if not re.match(r'^[A-Z]+[0-9]+$', cell):
                        return False
            
            # Handle styling
            if 'styling' in data:
                styling = data['styling']
                if not isinstance(styling, dict):
                    return False
                
            # Simulate success
            return True
    
    def test_complex_data_handling(self):
        """Test handling of complex data structures and edge cases."""
        generator = self.ComplexDataGenerator()
        
        # Test with valid raw data
        valid_raw_data = {
            'raw_data': [
                ['Name', 'Age', 'Score'],
                ['John', 30, 95],
                ['Alice', 25, 98]
            ]
        }
        assert generator.create_excel(valid_raw_data, 'output.xlsx')
        
        # Test with invalid raw data
        invalid_raw_data = {
            'raw_data': 'not a list'
        }
        assert not generator.create_excel(invalid_raw_data, 'output.xlsx')
        
        # Test with mixed row types (should fail)
        mixed_row_data = {
            'raw_data': [
                ['Name', 'Age', 'Score'],
                'John, 30, 95',  # String instead of list
                ['Alice', 25, 98]
            ]
        }
        assert not generator.create_excel(mixed_row_data, 'output.xlsx')
        
        # Test with valid formulas
        valid_formulas = {
            'raw_data': [['A', 'B', 'Sum']],
            'formulas': {
                'C2': '=SUM(A2:B2)',
                'C3': '=AVERAGE(A3:B3)'
            }
        }
        assert generator.create_excel(valid_formulas, 'output.xlsx')
        
        # Test with invalid formula cell references
        invalid_formula_refs = {
            'raw_data': [['A', 'B', 'Sum']],
            'formulas': {
                'C-2': '=SUM(A2:B2)',  # Invalid cell reference
                'C3': '=AVERAGE(A3:B3)'
            }
        }
        assert not generator.create_excel(invalid_formula_refs, 'output.xlsx')
        
        # Test with permission issues (path starting with /restricted/)
        assert not generator.create_excel(valid_raw_data, '/restricted/output.xlsx')
        
        # Test with readonly issues
        assert not generator.create_excel(valid_raw_data, '/readonly/output.xlsx')


class TestFormattingFeatures:
    """Test Excel formatting features through the generator interface."""
    
    class FormattedExcelGenerator(GeneratorInterface):
        """Generator with rich formatting capabilities."""
        
        def create_excel(self, data, output_path):
            """Create formatted Excel file with various styling options."""
            # Basic validation
            if not isinstance(data, dict) or 'content' not in data:
                return False
                
            content = data['content']
            if not isinstance(content, list) or not content:
                return False
                
            # Extract and validate formatting options
            formats = data.get('formats', {})
            headers = data.get('headers', True)
            sheet_name = data.get('sheet_name', 'Sheet1')
            
            # Validate sheet name (Excel limits to 31 chars)
            if not isinstance(sheet_name, str) or len(sheet_name) > 31:
                return False
                
            # Check for invalid formats
            if formats and not isinstance(formats, dict):
                return False
                
            # Check for unsupported format types
            supported_formats = ['bold', 'italic', 'border', 'color', 'background', 'number', 'date', 'percentage']
            if formats:
                for fmt_type in formats.keys():
                    if fmt_type not in supported_formats:
                        return False
            
            # Success
            return True
    
    def test_formatting_options(self):
        """Test various formatting options for Excel generation."""
        generator = self.FormattedExcelGenerator()
        
        # Test with basic content and no formatting
        basic_data = {
            'content': [
                ['Name', 'Value'],
                ['Item 1', 100],
                ['Item 2', 200]
            ]
        }
        assert generator.create_excel(basic_data, 'basic.xlsx')
        
        # Test with formatting options
        formatted_data = {
            'content': [
                ['Name', 'Value'],
                ['Item 1', 100],
                ['Item 2', 200]
            ],
            'formats': {
                'bold': [0, 0, 0, 1],  # First row (headers) and first column
                'color': {'range': [1, 1, 2, 2], 'value': '#FF0000'},  # Red for values
                'number': {'range': [1, 1, 2, 2], 'format': '#,##0.00'}  # Number format for values
            },
            'headers': True,
            'sheet_name': 'Sales Report'
        }
        assert generator.create_excel(formatted_data, 'formatted.xlsx')
        
        # Test with invalid format type
        invalid_format_type = {
            'content': [
                ['Name', 'Value'],
                ['Item 1', 100]
            ],
            'formats': {
                'sparkline': {'range': [1, 1, 1, 1]}  # Unsupported format
            }
        }
        assert not generator.create_excel(invalid_format_type, 'invalid.xlsx')
        
        # Test with too long sheet name
        long_sheet_name = {
            'content': [['A', 'B']],
            'sheet_name': 'This is an extremely long sheet name that should be rejected because it exceeds Excel limitation'
        }
        assert not generator.create_excel(long_sheet_name, 'long_name.xlsx')
        
        # Test with invalid content
        no_content = {
            'formats': {'bold': [0, 0, 0, 0]}
        }
        assert not generator.create_excel(no_content, 'no_content.xlsx')
        
        empty_content = {
            'content': []
        }
        assert not generator.create_excel(empty_content, 'empty.xlsx')
