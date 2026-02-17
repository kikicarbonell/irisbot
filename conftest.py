"""conftest.py - Pytest configuration and fixtures.

This file is automatically loaded by pytest before running tests.
It ensures the src directory is in sys.path for reliable imports.
"""

import sys
from pathlib import Path

# Add src directory to sys.path to ensure imports work
# This is more reliable than pytest.ini's pythonpath setting,
# especially when using coverage
project_root = Path(__file__).parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
