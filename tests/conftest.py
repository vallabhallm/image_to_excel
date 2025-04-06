import os
import sys
import pytest
import warnings

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def pytest_configure(config):
    """Configure pytest."""
    warnings.filterwarnings('ignore', category=DeprecationWarning, message='.*has no __module__ attribute')
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='importlib._bootstrap')
