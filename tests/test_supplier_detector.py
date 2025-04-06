"""Tests for the supplier detection functionality."""

import pytest
from src.utils.supplier_detector import SupplierDetector


@pytest.fixture
def mock_invoice_texts():
    """Create mock invoice text content for different suppliers."""
    return {
        "united_drug": """
            VAT REG NO. 2226527T
            DUBLIN:
            LIMERICK:
            BALLINA:
            Tel:
            Fax:
            Tel:
            Fax:
            Tel:
            Fax:
            (01) 4632300
            (01) 4632333
            (061) 315411
            (061) 315012
            (096) 72555
            (096) 72424
            Account
            Ord. No.
            Tote No.
            Date
            Time
            Type
            Invoice No.
            Your Ref.
            Van Route
            Invoice No.
            Account
            Your Ref.
            Date/Time
            Delivery Method:
            Taken By:
            QTY
            PACK
            DESCRIPTION
            V
            A
            T
            QTY
            PACK
            DESCRIPTION
            LOC
            Registered in Ireland as
            United Drug (Wholesale) Limited
            Company No. 046423
            See reverse for Terms and Conditions
        """,
        "genamed": """
            Suite 10591
            Fitzwilliam Business Centre
            26/27 Upper Pembroke Street
            Dublin 2.
            D02 X361
            NiAm Pharma Ltd trading as GenaMed
            Date
            Your Order #
            Description
            Quantity Unit Price Ship Via
            Terms VAT Rate
            09–12–2024
            PO Number
            WEX05/12/24
            C-Lock
            —46.7%
            Trisodium Citrate
            1
            € 165.00
            ND
            30 Days
            23%
        """,
        "iskus": """
            Iskus Health Ltd.
            4045 Kingswood Road
            Citywest Business Park
            Co. Dublin
            Tel: 01-4287895
            Fax: 01-4287876
            Email: info@iskushealth.com
            B BRAUN WELLSTONE LTD,
            B BRAUN WELLSTONE LTD
            3 NAAS ROAD IND PK,
            Dublin, Co. Dublin
            D12 T2T7
        """,
        "feehily": """
            Feehily's Medical Ltd
            Invoice for medical supplies
            Please pay within 30 days
        """
    }


class TestSupplierDetector:
    """Test suite for the supplier detector."""
    
    def test_detect_united_drug(self, mock_invoice_texts):
        """Test detection of United Drug invoices."""
        result = SupplierDetector.detect_supplier(mock_invoice_texts["united_drug"])
        assert result == "united_drug"
    
    def test_detect_genamed(self, mock_invoice_texts):
        """Test detection of Genamed invoices."""
        result = SupplierDetector.detect_supplier(mock_invoice_texts["genamed"])
        assert result == "genamed"
    
    def test_detect_iskus(self, mock_invoice_texts):
        """Test detection of Iskus invoices."""
        result = SupplierDetector.detect_supplier(mock_invoice_texts["iskus"])
        assert result == "iskus"
    
    def test_detect_feehily(self, mock_invoice_texts):
        """Test detection of Feehily invoices."""
        result = SupplierDetector.detect_supplier(mock_invoice_texts["feehily"])
        assert result == "feehily"
    
    def test_detect_unknown(self):
        """Test detection of unknown supplier."""
        result = SupplierDetector.detect_supplier("This is an invoice from an unknown supplier")
        assert result == "unknown"
    
    def test_empty_text(self):
        """Test handling of empty text."""
        result = SupplierDetector.detect_supplier("")
        assert result == "unknown"
        
        result = SupplierDetector.detect_supplier(None)
        assert result == "unknown"
