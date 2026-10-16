"""AST analyzer and complexity auditor for Python source files."""

from __future__ import annotations

import ast
from typing import Any, Dict, List, Set


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.complexity = 1
        self.max_nesting = 0
        self.current_nesting = 0
        self.functions_count = 0
        self.classes_count = 0
        self.imports: List[str] = []
        self.assigned_vars: Set[str] = set()
        self.referenced_vars: Set[str] = set()

    def _enter_nesting(self) -> None:
        self.current_nesting += 1
        if self.current_nesting > self.max_nesting:
            self.max_nesting = self.current_nesting

    def _exit_nesting(self) -> None:
        self.current_nesting -= 1

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.complexity += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_Try(self, node: ast.Try) -> None:
        self.complexity += len(node.handlers)
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.functions_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(f"{mod}.{alias.name}" if mod else alias.name)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.assigned_vars.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.referenced_vars.add(node.id)
        self.generic_visit(node)


def analyze_source(source: str) -> Dict[str, Any]:
    """Parse Python source code and calculate structural metrics."""
    lines = source.splitlines()
    loc = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    sloc = loc - blank_lines - comment_lines

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {
            "error": f"Syntax error at line {e.lineno}: {e.msg}",
            "loc": loc,
            "sloc": sloc,
            "cyclomatic_complexity": 0,
            "max_nesting_depth": 0,
            "functions": 0,
            "classes": 0,
            "unused_variables": [],
            "imports": [],
        }

    visitor = ComplexityVisitor()
    visitor.visit(tree)

    unused = sorted(list(visitor.assigned_vars - visitor.referenced_vars))

    return {
        "loc": loc,
        "sloc": sloc,
        "blank_lines": blank_lines,
        "comment_lines": comment_lines,
        "cyclomatic_complexity": visitor.complexity,
        "max_nesting_depth": visitor.max_nesting,
        "functions": visitor.functions_count,
        "classes": visitor.classes_count,
        "unused_variables": unused,
        "imports": visitor.imports,
    }
