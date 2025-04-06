"""Invoice parser module."""
import re
from loguru import logger
from typing import Dict, List, Union, Optional
from src.utils import extraction_config as config

class InvoiceParser:
    """Invoice parser class for extracting structured data from invoice text."""
    
    def __init__(self):
        """Initialize the invoice parser."""
        logger.debug("Initializing InvoiceParser")
        
    def parse_invoice_text(self, invoice_text: str) -> List[Dict]:
        """Parse invoice text and extract structured data.
        
        Args:
            invoice_text: Raw text from invoice
            
        Returns:
            List of dictionaries containing structured invoice data
        """
        try:
            # Extract supplier information
            supplier_info = self._extract_supplier_info(invoice_text)
            
            # Extract customer information
            customer_info = self._extract_customer_info(invoice_text)
            
            # Extract invoice details
            invoice_details = self._extract_invoice_details(invoice_text)
            
            # Extract financial details
            financial_details = self._extract_financial_details(invoice_text)
            
            # Extract item details
            items = self._extract_items(invoice_text)
            
            # If no items found, create a dummy item to hold all the invoice data
            if not items:
                items = [{}]
            
            # Create a result for each item
            results = []
            
            for item in items:
                item_dict = {
                    # Item details (with defaults)
                    'qty': item.get('qty', ''),
                    'description': item.get('description', ''),
                    'pack': item.get('pack', ''),
                    'price': item.get('price', ''),
                    'discount': item.get('discount', ''),
                    'vat': item.get('vat', ''),
                    'invoice_value': item.get('invoice_value', ''),
                    'batch': item.get('batch', ''),
                    'expiry_date': item.get('expiry_date', ''),
                    
                    # Add all extracted details
                    **supplier_info,
                    **customer_info,
                    **invoice_details,
                    **financial_details,
                }
                results.append(item_dict)
                
            return results
            
        except Exception as e:
            logger.error(f"Error parsing invoice text: {e}")
            return []
    
    def _extract_supplier_info(self, text: str) -> Dict[str, str]:
        """Extract all supplier information from invoice text."""
        # Look for typical supplier information patterns
        supplier_info = {}
        
        # Supplier name - usually at the top of the invoice
        supplier_info['supplier_name'] = self._extract_text_from_top(text, config.SUPPLIER_HEADER_LINES)
        
        # Supplier address - typically several lines after the name
        supplier_info['supplier_address'] = self._extract_address_from_top(text)
        
        # Contact information patterns
        supplier_info['supplier_tel'] = self._extract_with_patterns(text, config.TELEPHONE_PATTERNS)
        supplier_info['supplier_fax'] = self._extract_with_patterns(text, config.FAX_PATTERNS)
        supplier_info['supplier_email'] = self._extract_with_patterns(text, config.EMAIL_PATTERNS)
        
        return supplier_info
    
    def _extract_customer_info(self, text: str) -> Dict[str, str]:
        """Extract all customer information from invoice text."""
        customer_info = {
            'customer_name': '',
            'customer_address': ''
        }
        
        # First, try to find a distinct customer section
        customer_section = self._extract_customer_section(text)
        if customer_section:
            # Split it into lines and process
            lines = customer_section.strip().split('\n')
            if lines:
                customer_info['customer_name'] = lines[0].strip()
                address_lines = [line.strip() for line in lines[1:] if line.strip()]
                customer_info['customer_address'] = ", ".join(address_lines)
        else:
            # Fallback: look for terms that might indicate customer information
            customer_match = self._extract_with_patterns(text, config.CUSTOMER_SECTION_PATTERNS)
            if customer_match:
                customer_text = customer_match.strip()
                lines = customer_text.split('\n')
                if lines:
                    customer_info['customer_name'] = lines[0].strip()
                    customer_info['customer_address'] = ", ".join([l.strip() for l in lines[1:] if l.strip()])
        
        return customer_info
    
    def _extract_invoice_details(self, text: str) -> Dict[str, str]:
        """Extract all invoice details from invoice text."""
        invoice_details = {}
        
        # Extract invoice number
        invoice_details['invoice_number'] = self._extract_with_patterns(text, config.INVOICE_NUMBER_PATTERNS)
        
        # Extract invoice date
        invoice_details['invoice_date'] = self._extract_with_patterns(text, config.DATE_PATTERNS)
        
        # Extract purchase order number
        invoice_details['po_number'] = self._extract_with_patterns(text, config.PO_NUMBER_PATTERNS)
        
        return invoice_details
    
    def _extract_financial_details(self, text: str) -> Dict[str, str]:
        """Extract all financial details from invoice text."""
        financial_details = {}
        
        # Extract subtotal
        financial_details['subtotal'] = self._extract_with_patterns(text, config.SUBTOTAL_PATTERNS)
        
        # Extract tax/VAT
        financial_details['tax'] = self._extract_with_patterns(text, config.TAX_PATTERNS)
        
        # Extract total
        financial_details['total'] = self._extract_with_patterns(text, config.TOTAL_PATTERNS)
        
        return financial_details
    
    def _extract_items(self, text: str) -> List[Dict]:
        """Extract item details from invoice text."""
        # This is a complex extraction that looks for patterns of items in the invoice
        items = []
        
        # Extract the section that contains items
        item_section = self._extract_item_section(text)
        if item_section:
            # Process the extracted items
            items = self._process_item_section(item_section)
            
        return items
            
    def _extract_item_section(self, text: str) -> str:
        """Extract the section containing item details."""
        item_section = ""
        lines = text.strip().split('\n')
        item_lines = []
        in_item_section = False
        
        # Try to identify the item section
        for line in lines:
            # Check if we're at the start of the items section
            if not in_item_section:
                # Look for header-like line that marks the items section
                for pattern in config.ITEM_HEADER_PATTERNS:
                    if re.search(pattern, line.upper()):
                        in_item_section = True
                        break
                        
                # Specific format with QTY and DESCRIPTION
                if (("QTY" in line.upper() or "QUANTITY" in line.upper()) and 
                    ("DESCRIPTION" in line.upper() or "ITEM" in line.upper()) and
                    ("PRICE" in line.upper() or "RATE" in line.upper() or "AMOUNT" in line.upper())):
                    in_item_section = True
                    continue
                
                # Check if we've reached the end of the items section
                if in_item_section and any(marker in line.upper() for marker in config.ITEM_SECTION_END_MARKERS):
                    in_item_section = False
                    continue
                
                # If we're in an item section, add the line
                if in_item_section:
                    item_lines.append(line)
        
        # If we found an item section, handle it
        if item_lines:
            item_section = '\n'.join(item_lines)
            
        # If we didn't find a well-marked section, try a more general approach
        if not item_section:
            # Look for sections with multiple lines that might contain item details
            in_section = False
            current_section = []
            
            for line in lines:
                # Skip headers and footers
                if any(marker in line.upper() for marker in config.ITEM_SECTION_END_MARKERS):
                    if in_section:
                        # End of a potential item section
                        in_section = False
                        if len(current_section) >= 2:  # Need at least a couple lines
                            item_section = '\n'.join(current_section)
                            break
                        current_section = []
                    continue
                
                # Start a new section if we see a pattern that looks like an item
                if re.match(r"^\s*\d+", line) and len(line.split()) >= config.INVOICE_ITEM_MIN_LENGTH:
                    if not in_section:
                        in_section = True
                    current_section.append(line)
                elif in_section:
                    # Continue adding lines to current section
                    current_section.append(line)
                    
            # Final check if we ended in an item section
            if in_section and len(current_section) >= 2:
                item_section = '\n'.join(current_section)
                
        return item_section
        
    def _process_item_section(self, item_section: str) -> List[Dict]:
        """Process extracted item section into structured items."""
        items = []
        lines = item_section.strip().split('\n')
        
        # Skip any header lines
        start_idx = 0
        for i, line in enumerate(lines):
            if any(re.search(pattern, line.upper()) for pattern in config.ITEM_HEADER_PATTERNS):
                start_idx = i + 1
                break
        
        # Group lines into item entries
        # Some items may span multiple lines
        item_entries = []
        current_entry = []
        
        for line in lines[start_idx:]:
            # If line starts with a number (likely a quantity), it's a new item
            if re.match(r"^\s*\d+", line) and not line.strip().isdigit():
                if current_entry:
                    item_entries.append("\n".join(current_entry))
                current_entry = [line]
            elif current_entry:
                # Continue with current item
                current_entry.append(line)
            
        # Add the last entry
        if current_entry:
            item_entries.append("\n".join(current_entry))
        
        # Process each item entry
        for entry in item_entries:
            if not entry.strip():
                continue
            
            item = self._parse_item_entry(entry)
            if item:
                items.append(item)
                
        return items
    
    def _parse_item_entry(self, entry: str) -> Dict:
        """Parse a single item entry into a structured item."""
        item = {}
        entry_lines = entry.strip().split('\n')
        main_line = entry_lines[0].strip()
        
        # Extract quantity - try different patterns
        for pattern in config.ITEM_QTY_PATTERNS:
            qty_match = re.match(pattern, main_line)
            if qty_match:
                item['qty'] = qty_match.group(1).strip()
                break
                
        # Extract batch number and expiry date from additional lines
        batch, expiry = self._extract_batch_expiry(entry_lines)
        if batch:
            item['batch'] = batch
        if expiry:
            item['expiry_date'] = expiry
            
        # Extract other item details depending on available information
        if 'qty' in item:
            remaining_text = self._extract_remaining_text(main_line, item['qty'])
            # Try to extract price and description
            self._extract_price_and_description(item, remaining_text)
            
        return item
        
    def _extract_batch_expiry(self, entry_lines: List[str]) -> tuple:
        """Extract batch number and expiry date from item lines."""
        batch = ""
        expiry = ""
        
        # Only look at additional lines after the first one
        for line in entry_lines[1:]:
            # Look for batch number
            if not batch:
                for pattern in config.BATCH_PATTERNS:
                    batch_match = re.search(pattern, line, re.IGNORECASE)
                    if batch_match:
                        batch = batch_match.group(1).strip()
                        break
                        
            # Look for expiry date
            if not expiry:
                for pattern in config.EXPIRY_PATTERNS:
                    expiry_match = re.search(pattern, line, re.IGNORECASE)
                    if expiry_match:
                        expiry = expiry_match.group(1).strip()
                        break
                        
        return batch, expiry
    
    def _extract_remaining_text(self, line: str, qty: str) -> str:
        """Extract the remaining text after the quantity."""
        remaining = ""
        
        # Handle special format with "__"
        if '__' in line:
            parts = line.split('__', 1)
            if len(parts) > 1:
                remaining = parts[1].strip()
        else:
            # Regular format
            start_pos = line.find(qty) + len(qty)
            if start_pos < len(line):
                remaining = line[start_pos:].strip()
                
        return remaining
    
    def _extract_price_and_description(self, item: Dict, text: str) -> None:
        """Extract price and description from the remaining text."""
        if not text:
            return
            
        # Look for numeric values which might be prices
        price_matches = list(re.finditer(r"\d+\.\d+", text))
        
        if price_matches and len(price_matches) >= 2:
            # Multiple numbers found, assume the first is a dimension or feature
            # and the last is the price
            desc_end = price_matches[-2].start()
            item['price'] = price_matches[-2].group()
            item['invoice_value'] = price_matches[-1].group()
            
            # Check if there's a VAT code between description and price
            desc_text = text[:desc_end].strip()
            vat_match = re.search(r"(.*?)\s+([A-Z][0-9A-Z])\s*$", desc_text)
            if vat_match:
                item['description'] = vat_match.group(1).strip()
                item['vat'] = vat_match.group(2)
            else:
                item['description'] = desc_text
        elif price_matches:
            # Just one price found
            desc_end = price_matches[0].start()
            item['price'] = price_matches[0].group()
            
            # Check if there's a VAT code between description and price
            desc_text = text[:desc_end].strip()
            vat_match = re.search(r"(.*?)\s+([A-Z][0-9A-Z])\s*$", desc_text)
            if vat_match:
                item['description'] = vat_match.group(1).strip()
                item['vat'] = vat_match.group(2)
            else:
                item['description'] = desc_text
        else:
            # No clear price, just use everything as description
            # But still check for VAT code at the end
            vat_match = re.search(r"(.*?)\s+([A-Z][0-9A-Z])\s*$", text)
            if vat_match:
                item['description'] = vat_match.group(1).strip()
                item['vat'] = vat_match.group(2)
            else:
                item['description'] = text
            
        # If we have quantity and price but not invoice value, calculate it
        if 'qty' in item and 'price' in item and 'invoice_value' not in item:
            try:
                qty = float(item['qty'])
                price = float(item['price'].replace(',', ''))
                item['invoice_value'] = str(round(qty * price, 2))
            except ValueError:
                # Couldn't convert to float
                pass
    
    def _extract_text_from_top(self, text: str, num_lines: int = 1) -> str:
        """Extract the specified number of lines from the top of the text."""
        lines = text.strip().split('\n')
        return " ".join([lines[i].strip() for i in range(min(num_lines, len(lines)))])
    
    def _extract_address_from_top(self, text: str) -> str:
        """Extract address from the top of the text."""
        lines = text.strip().split('\n')
        
        # Skip the first line (usually company name)
        start_line = 1 if len(lines) > 1 else 0
        address_lines = []
        
        # Collect lines that look like an address
        for i in range(start_line, min(start_line + config.ADDRESS_MAX_LINES, len(lines))):
            line = lines[i].strip()
            # Stop if we hit something that's not an address line
            if not line or any(marker in line for marker in ["Tel:", "Fax:", "Email:"]):
                break
            address_lines.append(line)
            
        return ", ".join(address_lines)
    
    def _extract_customer_section(self, text: str) -> str:
        """Extract the customer section from invoice text."""
        lines = text.strip().split('\n')
        
        # Look for transitions between sections
        in_supplier_section = True
        supplier_end = 0
        
        # Find the end of supplier section (typically after contact details)
        for i, line in enumerate(lines):
            if in_supplier_section and any(marker in line for marker in config.SUPPLIER_SECTION_END_MARKERS):
                supplier_end = i + 1
                in_supplier_section = False
                break
        
        # If we didn't find a clear supplier end, look for the first gap
        if in_supplier_section:
            for i, line in enumerate(lines):
                if not line.strip() and i > 3:  # Skip early empty lines
                    supplier_end = i + 1
                    break
        
        # Look for the start of invoice details section
        invoice_start = len(lines)
        for i in range(supplier_end, len(lines)):
            if any(marker in line for marker in config.INVOICE_SECTION_START_MARKERS):
                invoice_start = i
                break
        
        # If identified correctly, the customer section is between these two
        if supplier_end < invoice_start:
            customer_section = "\n".join(lines[supplier_end:invoice_start])
            return customer_section.strip()
        
        return ""
    
    def _extract_with_patterns(self, text: str, patterns: List[str]) -> str:
        """Try multiple regex patterns to extract information."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
