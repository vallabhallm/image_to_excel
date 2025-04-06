"""Tests for supplier templates and field mappings."""

import pandas as pd
import pytest
from src.utils.supplier_templates import (
    get_prompt_template,
    get_field_mapping,
    get_expected_columns,
    get_post_processor,
    post_process_united_drug,
    post_process_genamed,
    post_process_iskus,
    post_process_feehily,
    post_process_unknown,
    SUPPLIER_PROMPTS,
    FIELD_MAPPINGS,
    EXPECTED_COLUMNS
)


class TestSupplierTemplates:
    """Test suite for supplier templates functionality."""
    
    def test_get_field_mapping(self):
        """Test retrieving field mappings for different suppliers."""
        # Test known supplier
        united_drug_mapping = get_field_mapping("united_drug")
        assert isinstance(united_drug_mapping, dict)
        assert "QTY" in united_drug_mapping
        assert united_drug_mapping["QTY"] == "qty"
        
        # Test another supplier
        genamed_mapping = get_field_mapping("genamed")
        assert isinstance(genamed_mapping, dict)
        assert "Quantity" in genamed_mapping
        
        # Test unknown supplier
        unknown_mapping = get_field_mapping("unknown_supplier")
        assert isinstance(unknown_mapping, dict)
        # Unknown should use the default mapping
        assert unknown_mapping == get_field_mapping("unknown")
    
    def test_get_prompt_template(self):
        """Test retrieving prompt templates for different suppliers."""
        # Test known supplier
        united_drug_prompt = get_prompt_template("united_drug")
        assert isinstance(united_drug_prompt, str)
        assert "United Drug" in united_drug_prompt
        
        # Test another supplier
        genamed_prompt = get_prompt_template("genamed")
        assert isinstance(genamed_prompt, str)
        assert "Genamed" in genamed_prompt
        
        # Test unknown supplier
        unknown_prompt = get_prompt_template("unknown_supplier")
        assert isinstance(unknown_prompt, str)
        # Unknown should use the default prompt
        assert unknown_prompt == get_prompt_template("unknown")
    
    def test_get_expected_columns(self):
        """Test retrieving expected columns for different suppliers."""
        # Test known supplier
        united_drug_cols = get_expected_columns("united_drug")
        assert isinstance(united_drug_cols, list)
        assert "qty" in united_drug_cols
        assert "description" in united_drug_cols
        
        # Test another supplier
        genamed_cols = get_expected_columns("genamed")
        assert isinstance(genamed_cols, list)
        assert "qty" in genamed_cols
        
        # Test unknown supplier
        unknown_cols = get_expected_columns("unknown_supplier")
        assert isinstance(unknown_cols, list)
        # Unknown should use the default columns
        assert unknown_cols == get_expected_columns("unknown")
    
    def test_get_post_processor(self):
        """Test retrieving post-processor functions for different suppliers."""
        # Test known supplier
        united_drug_processor = get_post_processor("united_drug")
        assert callable(united_drug_processor)
        
        # Test another supplier
        genamed_processor = get_post_processor("genamed")
        assert callable(genamed_processor)
        
        # Test unknown supplier
        unknown_processor = get_post_processor("unknown_supplier")
        assert callable(unknown_processor)
        # Unknown should use the default post-processor
        assert unknown_processor == get_post_processor("unknown")


def test_get_prompt_template():
    """Test getting prompt templates for different suppliers."""
    # Test existing supplier
    assert get_prompt_template("united_drug") == SUPPLIER_PROMPTS["united_drug"]
    assert get_prompt_template("genamed") == SUPPLIER_PROMPTS["genamed"]
    assert get_prompt_template("iskus") == SUPPLIER_PROMPTS["iskus"]
    assert get_prompt_template("feehily") == SUPPLIER_PROMPTS["feehily"]
    
    # Test unknown supplier
    assert get_prompt_template("nonexistent_supplier") == SUPPLIER_PROMPTS["unknown"]


def test_get_field_mapping():
    """Test getting field mappings for different suppliers."""
    # Test existing supplier
    assert get_field_mapping("united_drug") == FIELD_MAPPINGS["united_drug"]
    assert get_field_mapping("genamed") == FIELD_MAPPINGS["genamed"]
    
    # Test unknown supplier
    assert get_field_mapping("nonexistent_supplier") == FIELD_MAPPINGS["unknown"]


def test_get_expected_columns():
    """Test getting expected columns for different suppliers."""
    # Test existing supplier
    assert get_expected_columns("united_drug") == EXPECTED_COLUMNS["united_drug"]
    assert get_expected_columns("iskus") == EXPECTED_COLUMNS["iskus"]
    
    # Test unknown supplier
    assert get_expected_columns("nonexistent_supplier") == EXPECTED_COLUMNS["unknown"]


def test_get_post_processor():
    """Test getting post-processors for different suppliers."""
    # Test existing supplier
    assert get_post_processor("united_drug") == post_process_united_drug
    assert get_post_processor("genamed") == post_process_genamed
    assert get_post_processor("iskus") == post_process_iskus
    assert get_post_processor("feehily") == post_process_feehily
    
    # Test unknown supplier
    assert get_post_processor("nonexistent_supplier") == post_process_unknown


def test_post_process_united_drug():
    """Test post-processing for United Drug."""
    # Create sample DataFrame
    df = pd.DataFrame({
        "qty": [1, 2],
        "description": ["Item A", "Item B"],
        "price": [10.0, 20.0]
    })
    
    # Process the DataFrame
    result = post_process_united_drug(df)
    
    # Verify the result is correct
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert "qty" in result.columns


def test_post_process_genamed():
    """Test post-processing for Genamed with batch and expiry extraction."""
    # Create sample DataFrame with batch and expiry info in description
    df = pd.DataFrame({
        "qty": [1, 2],
        "description": [
            "Item A Batch: ABC123 Expiry Date: 01.02.2026", 
            "Item B Batch: XYZ789 Expiry Date: 30.11.2025"
        ],
        "price": [10.0, 20.0]
    })
    
    # Process the DataFrame
    result = post_process_genamed(df)
    
    # Verify the result has batch and expiry date extracted
    assert isinstance(result, pd.DataFrame)
    assert "batch" in result.columns
    assert "expiry_date" in result.columns
    assert result["batch"].iloc[0] == "ABC123"
    assert result["batch"].iloc[1] == "XYZ789"
    assert result["expiry_date"].iloc[0] == "01.02.2026"
    assert result["expiry_date"].iloc[1] == "30.11.2025"


def test_post_process_genamed_no_extraction_needed():
    """Test post-processing for Genamed when batch and expiry already exist."""
    # Create sample DataFrame with batch and expiry already as columns
    df = pd.DataFrame({
        "qty": [1, 2],
        "description": ["Item A", "Item B"],
        "price": [10.0, 20.0],
        "batch": ["ABC123", "XYZ789"],
        "expiry_date": ["01.02.2026", "30.11.2025"]
    })
    
    # Process the DataFrame
    result = post_process_genamed(df)
    
    # Verify the result keeps existing batch and expiry data
    assert isinstance(result, pd.DataFrame)
    assert result["batch"].iloc[0] == "ABC123"
    assert result["batch"].iloc[1] == "XYZ789"
    assert result["expiry_date"].iloc[0] == "01.02.2026"


def test_post_process_iskus():
    """Test post-processing for Iskus."""
    # Create sample DataFrame
    df = pd.DataFrame({
        "qty": [1, 2],
        "description": ["Item A", "Item B"],
        "price": [10.0, 20.0]
    })
    
    # Process the DataFrame
    result = post_process_iskus(df)
    
    # Verify the result is correctly processed
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert "qty" in result.columns


def test_post_process_feehily():
    """Test post-processing for Feehily."""
    # Create sample DataFrame
    df = pd.DataFrame({
        "qty": [1, 2],
        "description": ["Item A", "Item B"],
        "price": [10.0, 20.0]
    })
    
    # Process the DataFrame
    result = post_process_feehily(df)
    
    # Verify the result is correctly processed
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert "qty" in result.columns


def test_post_process_unknown():
    """Test post-processing for unknown supplier."""
    # Create sample DataFrame
    df = pd.DataFrame({
        "qty": [1, 2],
        "description": ["Item A", "Item B"],
        "price": [10.0, 20.0]
    })
    
    # Process the DataFrame
    result = post_process_unknown(df)
    
    # Verify the result is correctly processed
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert "qty" in result.columns
