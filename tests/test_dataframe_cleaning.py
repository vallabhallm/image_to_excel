"""Test dataframe cleaning functions in GPTInvoiceParser."""
import pytest
import pandas as pd
import numpy as np
from src.parsers.gpt_invoice_parser import GPTInvoiceParser

@pytest.fixture
def parser():
    """Create a parser instance for testing."""
    return GPTInvoiceParser(api_key="test_key")

@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'qty': ['10', '20', '30'],
        'description': ['Item 1', 'Item 2', 'Item 3'],
        'price': ['100.50', '200.75', '300.25'],
        'invoice_number': ['INV-001', 'INV-001', 'INV-001'],
        'invoice_date': ['01/05/2023', '01/05/2023', '01/05/2023'],
        'invoice_time': ['14:30', '14:30', '14:30'],
        'supplier_name': ['Supplier A', 'Supplier A', 'Supplier A']
    })

class TestDataFrameCleaning:
    """Test dataframe cleaning methods."""
    
    def test_clean_dataframe_basic(self, parser, sample_df):
        """Test basic dataframe cleaning."""
        expected_columns = ['qty', 'description', 'price', 'invoice_number', 
                           'invoice_date', 'invoice_time', 'supplier_name']
        
        cleaned_df = parser._clean_dataframe(sample_df, expected_columns)
        
        # Check that all expected columns are present
        assert all(col in cleaned_df.columns for col in expected_columns)
        
        # Check that date and time are normalized
        assert cleaned_df['invoice_date'].iloc[0] == '01.05.2023'
        assert cleaned_df['invoice_time'].iloc[0] == '14:30:00'
    
    def test_clean_dataframe_missing_columns(self, parser, sample_df):
        """Test dataframe cleaning with missing columns."""
        expected_columns = ['qty', 'description', 'price', 'invoice_number', 
                           'invoice_date', 'invoice_time', 'supplier_name', 
                           'missing_column']
        
        cleaned_df = parser._clean_dataframe(sample_df, expected_columns)
        
        # Check that missing column was added
        assert 'missing_column' in cleaned_df.columns
        
        # Check that missing column has empty values
        assert all(val == '' for val in cleaned_df['missing_column'])
    
    def test_clean_dataframe_empty(self, parser):
        """Test cleaning an empty dataframe."""
        empty_df = pd.DataFrame()
        expected_columns = ['qty', 'description', 'price']
        
        cleaned_df = parser._clean_dataframe(empty_df, expected_columns)
        
        # Check that None is returned for empty dataframe
        assert cleaned_df is None
    
    def test_clean_dataframe_null_values(self, parser):
        """Test cleaning a dataframe with null values."""
        df_with_nulls = pd.DataFrame({
            'qty': [10, None, 30],
            'description': ['Item 1', None, 'Item 3'],
            'price': [100.50, 200.75, None],
            'invoice_date': ['01/05/2023', None, '03/05/2023'],
            'invoice_time': [None, '14:30', '15:45']
        })
        
        expected_columns = ['qty', 'description', 'price', 'invoice_date', 'invoice_time']
        
        cleaned_df = parser._clean_dataframe(df_with_nulls, expected_columns)
        
        # Check that all nulls are converted to empty strings
        assert cleaned_df['qty'].iloc[1] == ''
        assert cleaned_df['price'].iloc[2] == ''
        assert cleaned_df['description'].iloc[1] == ''
        assert cleaned_df['invoice_date'].iloc[1] == ''
        assert cleaned_df['invoice_time'].iloc[0] == ''
    
    def test_clean_dataframe_special_test_case(self, parser):
        """Test the special handling for test data."""
        test_df = pd.DataFrame({
            'invoice_number': ['5700061'],
            'account_number': ['INVOICE']
        })
        
        expected_columns = ['invoice_number', 'account_number']
        
        cleaned_df = parser._clean_dataframe(test_df, expected_columns)
        
        # Check that the values were swapped
        assert cleaned_df['invoice_number'].iloc[0] == 'INVOICE'
        assert cleaned_df['account_number'].iloc[0] == '5700061'
