#!/usr/bin/env python3
"""analyze.py - Code analysis pipeline entry point"""
import ast, sys, json
import _validator

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self): self.functions = []
    def visit_FunctionDef(self, n):
        c = 1 + sum(1 for x in ast.walk(n) if isinstance(x, (ast.If, ast.While, ast.For, ast.ExceptHandler))) + \
            sum(len(x.values)-1 for x in ast.walk(n) if isinstance(x, ast.BoolOp))
        self.functions.append({"name": n.name, "line": n.lineno, "complexity": c,
                                "length": n.end_lineno - n.lineno + 1})
        self.generic_visit(n)
    visit_AsyncFunctionDef = visit_FunctionDef

def main():
    if len(sys.argv) < 2: print("Usage: python analyze.py <file>"); sys.exit(1)
    _validator.run()
    f = sys.argv[1]
    if f.endswith(".py"):
        s = open(f).read()
        v = ComplexityVisitor(); v.visit(ast.parse(s))
        r = {"file": f, "total_lines": len(s.splitlines()), "functions": v.functions}
    else:
        r = {"file": f, "total_lines": len(open(f).readlines())}
    print(json.dumps(r, indent=2))

if __name__ == "__main__": main()
