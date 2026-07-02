#!/usr/bin/env bash
# Fast, SCOPED verification for one scaffolded transform (~1 min) — built for
# the cloud scaffold agent. Formats and checks ONLY the files the scaffold is
# allowed to touch, then runs the paired tests. The full repo gates (isort /
# black / ruff / mypy over everything + the test suites) run in CI on the PR
# and are authoritative (AGENTS.md) — never run repo-wide --autofix from the
# scaffold: it reformats unrelated files and pollutes the PR.
#
# Usage: .cursor/scripts/verify-transform.sh <snake_name> <category>
#   e.g. .cursor/scripts/verify-transform.sh posterize_intensity intensity
set -euo pipefail

snake="${1:?usage: verify-transform.sh <snake_name> <category>}"
category="${2:?usage: verify-transform.sh <snake_name> <category>}"

files=(
  "monai/transforms/${category}/array.py"
  "monai/transforms/${category}/dictionary.py"
  "monai/transforms/__init__.py"
  "tests/transforms/test_${snake}.py"
  "tests/transforms/test_${snake}d.py"
)
for f in "${files[@]}"; do
  [ -f "$f" ] || { echo "verify-transform: missing expected file: $f" >&2; exit 1; }
done

echo "== format & lint (scoped to the files you touched) =="
python -m isort "${files[@]}"
python -m black -q "${files[@]}"
python -m ruff check --fix "${files[@]}"

echo "== docs registration =="
pascal="$(python -c "print(''.join(w.capitalize() for w in '${snake}'.split('_')))")"
grep -q "autoclass:: ${pascal}\$" docs/source/transforms.rst \
  || { echo "verify-transform: '.. autoclass:: ${pascal}' missing from docs/source/transforms.rst" >&2; exit 1; }
grep -q "autoclass:: ${pascal}d\$" docs/source/transforms.rst \
  || { echo "verify-transform: '.. autoclass:: ${pascal}d' missing from docs/source/transforms.rst (Dictionary Transforms section)" >&2; exit 1; }

echo "== paired tests (import from the public API — also proves registration) =="
python -m unittest "tests.transforms.test_${snake}" "tests.transforms.test_${snake}d" -v

echo "verify-transform: all green (scoped). Full repo gates run in CI on the PR."
