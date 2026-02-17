#!/usr/bin/env python3
"""Custom pre-commit hook: Check for type hints in public functions.

Validates:
    - Public functions have type hints on parameters and return
    - Async functions have type hints
    - Skips __init__ and short private functions
"""

import ast
import logging
import sys

logger = logging.getLogger(__name__)


class TypeHintChecker(ast.NodeVisitor):
    """Check for type hints in public functions."""

    def __init__(self, filename: str) -> None:
        """Initialize the type hint checker.

        Args:
            filename: Path to the file being checked.
        """
        self.filename = filename
        self.errors: list[str] = []

    def check_function_hints(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        is_async: bool = False,
    ) -> None:
        """Check if function has type hints.

        Args:
            node: AST function node to check.
            is_async: Whether this is an async function.
        """
        if node.name.startswith("_"):
            # Skip private functions
            return

        # Skip __init__, __repr__, etc. - they can be simpler
        if node.name.startswith("__"):
            return

        # Check return annotation
        if node.returns is None:
            func_type = "async function" if is_async else "function"
            self.errors.append(
                f"⚠️  {self.filename}:{node.lineno}: "
                f"Public {func_type} '{node.name}' missing return type hint"
            )

        # Check parameter annotations (skip self/cls)
        for arg in node.args.args:
            if arg.arg in ("self", "cls"):
                continue
            if arg.annotation is None:
                func_type = "async function" if is_async else "function"
                self.errors.append(
                    f"⚠️  {self.filename}:{node.lineno}: "
                    f"Parameter '{arg.arg}' in '{node.name}' missing type hint"
                )

    def visit_FunctionDef(self, node) -> None:
        """Visit function definition node.

        Args:
            node: AST function node.
        """
        self.check_function_hints(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node) -> None:
        """Visit async function definition node.

        Args:
            node: AST async function node.
        """
        self.check_function_hints(node, is_async=True)
        self.generic_visit(node)


def check_type_hints(filename: str) -> bool:
    """Check file for missing type hints.

    Args:
        filename: Path to the file to check.

    Returns:
        True to not block commit (warnings only).
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        checker = TypeHintChecker(filename)
        checker.visit(tree)

        # Only show warnings, don't fail (type hints are gradually added)
        for error in checker.errors:
            logger.warning(error)

        # Return True to not block commit (warnings only)
        return True
    except SyntaxError as e:
        logger.warning(f"⚠️  {filename}: Syntax error - {e}")
        return False


if __name__ == "__main__":
    retval = 0
    for filename in sys.argv[1:]:
        if filename.endswith(".py"):
            if not check_type_hints(filename):
                retval = 1

    sys.exit(retval)
