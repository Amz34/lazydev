"""Command-line interface for lazydev."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List

from lazydev.analyzer import analyze_source
from lazydev.detector import RedundancyDetector
from lazydev.pruner import simplify_code


def audit_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    metrics = analyze_source(content)
    detector = RedundancyDetector(content)
    findings = detector.run()

    return {
        "file": path,
        "metrics": metrics,
        "findings": findings,
    }


def find_python_files(path: str) -> List[str]:
    if os.path.isfile(path):
        return [path] if path.endswith(".py") else []
    py_files = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "__pycache__", "build", "dist"}]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return sorted(py_files)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="lazydev",
        description="Audit codebases for over-engineering, unnecessary complexity, and bloat.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Audit command
    audit_cmd = subparsers.add_parser("audit", help="Audit files or directories for bloat and complexity.")
    audit_cmd.add_argument("paths", nargs="+", help="Files or directories to scan.")
    audit_cmd.add_argument("--json", action="store_true", help="Output results in JSON format.")
    audit_cmd.add_argument("--max-complexity", type=int, default=15, help="Warn if cyclomatic complexity exceeds threshold.")

    # Prune command
    prune_cmd = subparsers.add_parser("prune", help="Clean up redundant comments and blank lines non-destructively.")
    prune_cmd.add_argument("paths", nargs="+", help="Files or directories to process.")
    prune_cmd.add_argument("--dry-run", action="store_true", help="Print simplified code to stdout instead of modifying in-place.")

    args = parser.parse_args()

    if args.command == "audit":
        all_files: List[str] = []
        for p in args.paths:
            all_files.extend(find_python_files(p))

        if not all_files:
            print("No Python files found to audit.", file=sys.stderr)
            return 1

        results = [audit_file(f) for f in all_files]

        if args.json:
            print(json.dumps(results, indent=2))
            return 0

        total_findings = sum(len(r["findings"]) for r in results)
        print(f"Audited {len(all_files)} file(s). Found {total_findings} anti-pattern/bloat finding(s).\n")

        for r in results:
            m = r["metrics"]
            fname = r["file"]
            high_complexity = m.get("cyclomatic_complexity", 0) > args.max_complexity
            status = "WARN" if (r["findings"] or high_complexity) else "OK"
            print(f"[{status}] {fname}")
            print(f"  SLOC: {m.get('sloc', 0)} (Total lines: {m.get('loc', 0)}) | Complexity: {m.get('cyclomatic_complexity', 0)} | Nesting: {m.get('max_nesting_depth', 0)}")
            
            for f in r["findings"]:
                sev = f["severity"].upper()
                print(f"  - [{sev}] {f['pattern']}: {f['message']}")
            print()

        return 0

    elif args.command == "prune":
        all_files = []
        for p in args.paths:
            all_files.extend(find_python_files(p))

        for f in all_files:
            with open(f, "r", encoding="utf-8") as fh:
                orig = fh.read()
            simplified = simplify_code(orig)
            if args.dry_run:
                print(f"--- {f} (simplified) ---")
                print(simplified)
            else:
                if orig != simplified:
                    with open(f, "w", encoding="utf-8") as fh:
                        fh.write(simplified)
                    print(f"Pruned: {f}")
                else:
                    print(f"No changes: {f}")

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
