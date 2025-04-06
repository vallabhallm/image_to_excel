"""Supplier detection module for invoice processing."""

import re
from loguru import logger


class SupplierDetector:
    """Detects supplier type from invoice text content."""

    SUPPLIER_PATTERNS = {
        "united_drug": [
            r"United Drug \(Wholesale\) Limited",
            r"VAT REG NO\. 2226527T",
            r"Magna Business Park, Citywest Road, Dublin 24"
        ],
        "genamed": [
            r"NiAm Pharma Ltd trading as GenaMed",
            r"Fitzwilliam Business Centre",
            r"info@genamed\.ie"
        ],
        "iskus": [
            r"Iskus Health Ltd",
            r"Citywest Business Park",
            r"info@iskushealth\.com"
        ],
        "feehily": [
            r"Feehily",
            r"Fehily"
        ]
    }

    @classmethod
    def detect_supplier(cls, text_content):
        """
        Detect supplier from text content.
        
        Args:
            text_content: Raw text extracted from invoice
            
        Returns:
            supplier_type: String identifier for the supplier (or "unknown")
        """
        if not text_content:
            logger.warning("Empty text content provided for supplier detection")
            return "unknown"
            
        # Calculate matches for each supplier pattern
        match_scores = {}
        
        for supplier, patterns in cls.SUPPLIER_PATTERNS.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    matches += 1
            
            match_scores[supplier] = matches
        
        # Find supplier with highest match score
        best_supplier = max(match_scores.items(), key=lambda x: x[1])
        supplier_type, score = best_supplier
        
        # Only return if we have at least one match
        if score > 0:
            logger.info(f"Detected supplier: {supplier_type} (score: {score})")
            return supplier_type
        else:
            logger.warning("Could not detect supplier type from invoice content")
            return "unknown"
