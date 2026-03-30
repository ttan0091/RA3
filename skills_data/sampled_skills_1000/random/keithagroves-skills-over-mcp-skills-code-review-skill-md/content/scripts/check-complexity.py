#!/usr/bin/env python3
"""
Code complexity checker.

Analyzes Python files for cyclomatic complexity and reports functions
that exceed the threshold.

Usage:
    python check-complexity.py <file_or_directory> [--threshold=10]
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor that calculates cyclomatic complexity."""

    def __init__(self):
        self.functions: List[Tuple[str, int, int]] = []
        self._current_complexity = 0
        self._current_function = None
        self._current_line = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function(node)

    def _visit_function(self, node):
        old_complexity = self._current_complexity
        old_function = self._current_function
        old_line = self._current_line

        self._current_complexity = 1  # Base complexity
        self._current_function = node.name
        self._current_line = node.lineno

        self.generic_visit(node)

        self.functions.append(
            (self._current_function, self._current_line, self._current_complexity)
        )

        self._current_complexity = old_complexity
        self._current_function = old_function
        self._current_line = old_line

    def visit_If(self, node: ast.If):
        self._current_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self._current_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self._current_complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self._current_complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        # Count each 'and'/'or' as a decision point
        self._current_complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension):
        self._current_complexity += 1
        if node.ifs:
            self._current_complexity += len(node.ifs)
        self.generic_visit(node)


def analyze_file(filepath: Path, threshold: int = 10) -> List[dict]:
    """Analyze a Python file for complexity."""
    try:
        source = filepath.read_text()
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        return [{"file": str(filepath), "error": f"Syntax error: {e}"}]

    visitor = ComplexityVisitor()
    visitor.visit(tree)

    results = []
    for name, line, complexity in visitor.functions:
        if complexity > threshold:
            results.append({
                "file": str(filepath),
                "function": name,
                "line": line,
                "complexity": complexity,
                "threshold": threshold,
            })

    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    path = Path(sys.argv[1])
    threshold = 10

    for arg in sys.argv[2:]:
        if arg.startswith("--threshold="):
            threshold = int(arg.split("=")[1])

    results = []

    if path.is_file():
        results = analyze_file(path, threshold)
    elif path.is_dir():
        for pyfile in path.rglob("*.py"):
            results.extend(analyze_file(pyfile, threshold))
    else:
        print(f"Error: {path} not found")
        sys.exit(1)

    if results:
        print(f"Functions exceeding complexity threshold of {threshold}:\n")
        for r in results:
            if "error" in r:
                print(f"  {r['file']}: {r['error']}")
            else:
                print(
                    f"  {r['file']}:{r['line']} - {r['function']}() "
                    f"complexity={r['complexity']}"
                )
        sys.exit(1)
    else:
        print(f"All functions are within complexity threshold of {threshold}")
        sys.exit(0)


if __name__ == "__main__":
    main()
