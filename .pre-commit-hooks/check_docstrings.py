#!/usr/bin/env python3
"""
Custom pre-commit hook: Check for docstrings in public functions.

Validates:
- Public functions (not starting with _) have docstrings
- Async functions have docstrings
- Classes have docstrings
"""

import ast
import sys
from pathlib import Path


class DocstringChecker(ast.NodeVisitor):
    """Check for missing docstrings in public functions/classes."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.errors = []
    
    def visit_FunctionDef(self, node):
        if not node.name.startswith('_'):  # Public function
            if not ast.get_docstring(node):
                self.errors.append(
                    f"❌ {self.filename}:{node.lineno}: "
                    f"Public function '{node.name}' missing docstring"
                )
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        if not node.name.startswith('_'):  # Public async function
            if not ast.get_docstring(node):
                self.errors.append(
                    f"❌ {self.filename}:{node.lineno}: "
                    f"Public async function '{node.name}' missing docstring"
                )
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        if not node.name.startswith('_'):  # Public class
            if not ast.get_docstring(node):
                self.errors.append(
                    f"❌ {self.filename}:{node.lineno}: "
                    f"Public class '{node.name}' missing docstring"
                )
        self.generic_visit(node)


def check_docstrings(filename: str) -> bool:
    """Check file for missing docstrings."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        checker = DocstringChecker(filename)
        checker.visit(tree)
        
        for error in checker.errors:
            print(error)
        
        return len(checker.errors) == 0
    except SyntaxError as e:
        print(f"⚠️  {filename}: Syntax error - {e}")
        return False


if __name__ == '__main__':
    retval = 0
    for filename in sys.argv[1:]:
        if filename.endswith('.py'):
            if not check_docstrings(filename):
                retval = 1
    
    sys.exit(retval)
