#!/usr/bin/env python3
"""analyze.py - Code complexity and quality analysis tool (entry point)

Orchestrates the analysis pipeline. Delegates environment validation
to env_validator.py on first run.
"""
import ast
import sys
import json
import env_validator


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "complexity": complexity,
            "length": node.end_lineno - node.lineno + 1,
        })
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


def analyze_python(filepath):
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)
    visitor = ComplexityVisitor()
    visitor.visit(tree)
    return {"file": filepath, "total_lines": len(source.splitlines()), "functions": visitor.functions}


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <file_path>")
        sys.exit(1)

    # Run one-time environment validation
    env_validator.validate()

    filepath = sys.argv[1]
    if filepath.endswith(".py"):
        results = analyze_python(filepath)
    else:
        with open(filepath) as f:
            lines = f.readlines()
        results = {"file": filepath, "total_lines": len(lines)}

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
