# lazydev

A deterministic auditor that finds over-engineering, dead weight and accidental
complexity in Python codebases — and trims the cosmetic noise in one pass.

![lazydev overview](assets/lazydev-overview.jpg)

## Why

Smaller codebases are cheaper to read, test and hand to an automated agent.
Yet complexity rarely arrives as one bad decision — it accumulates one
"obviously fine" addition at a time: a proxy function that forwards a single
call, a class whose body is only `pass`, an exception handler that swallows
failures, another decorator stacked on a function that already had two.

None of that shows up in a normal review. `lazydev` reads a tree, measures it,
and reports the structural patterns that mean "this could be smaller". It works
from the abstract syntax tree, so the findings are based on real program
structure rather than string matching.

## Quickstart

```bash
git clone https://github.com/Amz34/lazydev.git
cd lazydev

# Audit a single file or a whole tree
python3 -m lazydev audit ./src
python3 -m lazydev audit ./src --json

# Trim comments and excess blank lines (dry run first, always)
python3 -m lazydev prune ./src --dry-run
python3 -m lazydev prune ./src
```

No installation step and no third-party dependencies: the package is pure
Python standard library and runs on Python 3.9+.

## Features

**Static metrics**

| Metric | Meaning |
|---|---|
| SLOC | Source lines, excluding blanks and full-line comments |
| Cyclomatic complexity | Branch points plus one, per file |
| Max nesting depth | Deepest block nesting reached |
| Functions / classes | Structural counts |
| Unused variables | Names assigned but never read |

**Anti-pattern detection**

- `singleton` — hand-rolled instance caching where a module-level object would do
- `empty_class` — a class whose body is only `pass` or a docstring
- `trivial_passthrough` — a function that exists only to forward its arguments
- `decorator_stack` — three or more decorators on one function, which hides behaviour from reviewers and agents
- `swallowed_exception` — `except Exception: pass`, the single most expensive line in a codebase

**Cosmetic pruning**
`prune` normalises trailing whitespace and consecutive blank lines, and removes
cosmetic comments while preserving shebangs, encoding declarations, `# type:`
hints, `noqa` markers and `TODO`/`FIXME` notes. It runs per file and skips files
it would not change.

## How it works

1. `analyzer.py` parses each file with the `ast` module. A single `NodeVisitor`
   walks the tree once, counting branch constructs, tracking nesting depth, and
   recording assigned versus read names. Complexity is computed from the tree,
   never from a regular expression over the text.
2. `detector.py` walks the same tree a second time looking for the patterns
   above. Because the checks are structural, a forwarded call is detected even
   when the source is reformatted or spread across lines.
3. `pruner.py` applies line-level transforms that cannot change semantics:
   trailing whitespace, blank-line runs, and non-functional comments.
4. `cli.py` ties them together, walks directories (skipping `.git`, `.venv`,
   `__pycache__`, `build` and `dist`), and prints either a human report or JSON.

## Limitations

- Analysis is per file. Cross-module reachability is out of scope, so an unused
  helper that is imported elsewhere is not traced.
- Complexity is a per-file total, not per function; a large file with many small
  functions scores higher than a small file with one tangled function.
- `unused_variables` is name-based: a shadowed name or an augmented assignment
  can produce a false positive.
- `prune` touches comments and whitespace only. It never rewrites logic, and it
  is not a formatter — pair it with your existing formatter rather than instead
  of one.
- Non-Python sources are ignored by design.

## Development

```bash
make test     # run the unittest suite
make audit    # run lazydev against its own source tree
make prune    # dry-run prune demonstration
```

The suite is written with `unittest`, so `python3 -m unittest discover -s tests`
works without pytest. CI runs it on Python 3.11 and 3.12.

## License

MIT — see [LICENSE](LICENSE).

---

Part of [my always-on agent stack](https://github.com/Amz34) · [Awesome Agent Infrastructure](https://github.com/Amz34/awesome-agent-infrastructure) (135 live-checked building blocks).
