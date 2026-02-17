#!/usr/bin/env python3
"""
Custom pre-commit hook: Check for forbidden imports and patterns.

Validates:
- No Selenium imports (must use Playwright)
- No requests library (must use aiohttp)
- No hardcoded credentials in code
- No hardcoded file paths (must use pathlib)
- No print() statements (must use logging)
"""

import re
import sys
from pathlib import Path


def check_forbidden_imports(filename: str) -> bool:
    """Check for Selenium and requests imports."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    errors = []
    
    # Check for Selenium
    if re.search(r'\bfrom\s+selenium\b|\bimport\s+selenium\b', content):
        errors.append(f"❌ {filename}: Uses Selenium (use Playwright instead)")
    
    # Check for requests library
    if re.search(r'\bfrom\s+requests\b|\bimport\s+requests\b', content):
        errors.append(f"❌ {filename}: Uses requests (use aiohttp instead)")
    
    # Check for hardcoded credentials
    if re.search(r'(password|pwd|secret|token|key)\s*=\s*["\']', content, re.IGNORECASE):
        # Exclude common patterns like "password_field", "password_input"
        if not re.search(r'(password_field|password_input|password_label)', content, re.IGNORECASE):
            errors.append(f"⚠️  {filename}: Possible hardcoded credentials")
    
    # Check for hardcoded file paths (strings with /)
    hardcoded_paths = re.findall(r'["\']([./][^"\']*)["\']', content)
    for path in hardcoded_paths:
        # Skip common patterns
        if path.startswith('/iniciar-sesion') or path.startswith('/proyecto'):
            continue  # These are web URLs, not file paths
        if '.json' in path or '.html' in path or '.csv' in path:
            errors.append(f"⚠️  {filename}: Possible hardcoded path '{path}' (use pathlib)")
    
    # Check for print statements (should use logging)
    if re.search(r'\bprint\s*\(', content):
        # Exclude print statements in docstrings and comments mostly
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(r'^\s*print\s*\(', line):
                errors.append(f"⚠️  {filename}:{i}: Use logging instead of print()")
    
    for error in errors:
        print(error)
    
    return len(errors) == 0


if __name__ == '__main__':
    retval = 0
    for filename in sys.argv[1:]:
        if filename.endswith('.py'):
            if not check_forbidden_imports(filename):
                retval = 1
    
    sys.exit(retval)
