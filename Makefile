.PHONY: test audit prune run clean

PY ?= python3

test:
	$(PY) -m unittest discover -s tests -v

audit:
	$(PY) -m lazydev audit lazydev

prune:
	$(PY) -m lazydev prune lazydev --dry-run

run:
	$(PY) -m lazydev --help

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
