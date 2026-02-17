"""conftest.py - Pytest configuration and fixtures.

This file is automatically loaded by pytest before running tests.
It ensures the project root is in sys.path for reliable imports.
"""

import sys
from pathlib import Path

# Add project root to sys.path to ensure imports work
# This is more reliable than pytest.ini's pythonpath setting,
# especially when using coverage
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
