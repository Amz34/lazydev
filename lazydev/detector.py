"""Pattern detectors for over-engineering and boilerplate code."""

from __future__ import annotations

import ast
import re
from typing import Any, Dict, List


class RedundancyDetector:
    """Scans AST and tokens for common over-engineering anti-patterns."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.findings: List[Dict[str, Any]] = []

    def run(self) -> List[Dict[str, Any]]:
        self.findings.clear()
        self._check_singleton_pattern()
        self._check_empty_abstractions()
        self._check_pass_through_functions()
        self._check_overused_decorators()
        self._check_excessive_try_except()
        return self.findings

    def _check_singleton_pattern(self) -> None:
        if "__instance" in self.source or "cls._instance" in self.source:
            self.findings.append({
                "category": "overengineering",
                "pattern": "singleton",
                "severity": "medium",
                "message": "Custom singleton pattern detected. A standard module-level instance or plain function is usually simpler.",
            })

    def _check_empty_abstractions(self) -> None:
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes that only inherit and have 'pass' or just docstring
                stmts = [s for s in node.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
                if len(stmts) == 1 and isinstance(stmts[0], ast.Pass):
                    self.findings.append({
                        "category": "boilerplate",
                        "pattern": "empty_class",
                        "severity": "low",
                        "message": f"Class '{node.name}' has no logic beyond pass/docstring. Verify if a dictionary or NamedTuple is sufficient.",
                    })

    def _check_pass_through_functions(self) -> None:
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # A single return statement that just calls another function with identical arguments
                stmts = [s for s in node.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
                if len(stmts) == 1 and isinstance(stmts[0], ast.Return):
                    ret_val = stmts[0].value
                    if isinstance(ret_val, ast.Call) and isinstance(ret_val.func, ast.Name):
                        if len(node.args.args) == len(ret_val.args):
                            self.findings.append({
                                "category": "wrapper_bloat",
                                "pattern": "trivial_passthrough",
                                "severity": "medium",
                                "message": f"Function '{node.name}' directly forwards calls to '{ret_val.func.id}'. Consider calling the target directly.",
                            })

    def _check_overused_decorators(self) -> None:
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.decorator_list) >= 3:
                    self.findings.append({
                        "category": "complexity",
                        "pattern": "decorator_stack",
                        "severity": "low",
                        "message": f"Function '{node.name}' has {len(node.decorator_list)} decorators. Deep decorator stacks hinder agent observability.",
                    })

    def _check_excessive_try_except(self) -> None:
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id == "Exception"):
                        # Check if handler just contains pass
                        if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                            self.findings.append({
                                "category": "antipattern",
                                "pattern": "swallowed_exception",
                                "severity": "high",
                                "message": "Bare or generic Exception handler silently swallowing errors with pass.",
                            })
