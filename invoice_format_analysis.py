#!/usr/bin/env python
"""Script to analyze invoice formats from different suppliers."""

import os
import sys
import fitz  # PyMuPDF
import pandas as pd
from collections import defaultdict


def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def analyze_invoice_directory(base_dir):
    """Analyze invoice formats from different suppliers."""
    # Get all subdirectories (supplier types)
    suppliers = [d for d in os.listdir(base_dir) 
               if os.path.isdir(os.path.join(base_dir, d))]
    
    results = {}
    
    print(f"Found {len(suppliers)} supplier directories")
    
    for supplier in suppliers:
        supplier_dir = os.path.join(base_dir, supplier)
        invoice_files = [f for f in os.listdir(supplier_dir) 
                       if f.lower().endswith('.pdf')]
        
        if not invoice_files:
            print(f"No PDF invoices found for {supplier}")
            continue
        
        print(f"\n{'='*80}")
        print(f"Analyzing {supplier} - Found {len(invoice_files)} invoices")
        print(f"{'='*80}")
        
        # Just analyze the first invoice as a sample
        sample_file = invoice_files[0]
        sample_path = os.path.join(supplier_dir, sample_file)
        
        print(f"Sample invoice: {sample_file}")
        text_content = extract_text_from_pdf(sample_path)
        
        # Print first 1000 chars as preview
        preview = text_content[:1000].replace('\n', '\\n')
        print(f"Text preview: {preview}...")
        
        # Basic structure analysis
        lines = text_content.split('\n')
        print(f"Total lines: {len(lines)}")
        
        # Look for potential table headers or data patterns
        potential_headers = []
        for i, line in enumerate(lines):
            # Skip very short lines
            if len(line.strip()) < 5:
                continue
                
            # Look for lines that might be headers (containing multiple words with spaces)
            words = line.strip().split()
            if 3 <= len(words) <= 10 and any(w.isalpha() for w in words):
                potential_headers.append((i, line.strip()))
        
        print(f"\nPotential column headers/data patterns:")
        for idx, header in potential_headers[:10]:  # Show first 10 potential headers
            print(f"Line {idx}: {header}")
        
        results[supplier] = {
            'sample_file': sample_file,
            'line_count': len(lines),
            'potential_headers': potential_headers[:10]
        }
    
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        invoice_dir = sys.argv[1]
    else:
        invoice_dir = "data/INVOICES FOR WELLSTONE DRUGS PURCHASES (2024)"
    
    if not os.path.exists(invoice_dir):
        print(f"Directory not found: {invoice_dir}")
        sys.exit(1)
    
    print(f"Analyzing invoices in: {invoice_dir}")
    analyze_invoice_directory(invoice_dir)
