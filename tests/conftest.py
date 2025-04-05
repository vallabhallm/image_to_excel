import pytest
import warnings

def pytest_configure(config):
    """Configure pytest."""
    warnings.filterwarnings('ignore', category=DeprecationWarning, message='.*has no __module__ attribute')
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='importlib._bootstrap')
