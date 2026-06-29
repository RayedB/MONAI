# AGENTS.md — MONAI contributor & agent guide

**MONAI** is a PyTorch-based, Apache-2.0 framework for deep learning in medical imaging. The
codebase is large, active, **review-gated** (every change is human-reviewed and merged) and
**type-checked** (mypy + pytype).

## Where transform work lives

- Transforms live in `monai/transforms/<category>/array.py` and `dictionary.py`.
  Categories: `intensity`, `spatial`, `croppad`, `post`, `io`, `utility`, `signal`, `smooth_field`,
  `regularization`, `lazy` (each has both files; `meta_utility` is dictionary-only).
- A transform is **registered in two places**: `monai/transforms/__init__.py` (public API) **and**
  `docs/source/transforms.rst` (autoclass entry).
- **Read-only — do not modify:** `monai/networks/`, `monai/csrc/`, `monai/data/`,
  `monai/engines/`, `monai/apps/`, other transform categories, CI, and config files. Stop and ask
  if a task seems to need them.

## The golden path (adding a transform)

1. **Read the closest existing transform _pair_ first** (reference: `ShiftIntensity` /
   `ShiftIntensityd` in `intensity/`) and mirror it.
2. Implement the **array class** (base `Transform`, or `RandomizableTransform` if stochastic).
3. Implement the **`d`-suffixed dictionary wrapper** (base `MapTransform`).
4. Add the **triple alias** `FooD = FooDict = Food` at the bottom of `dictionary.py`.
5. **Register** in `monai/transforms/__init__.py` **and** `docs/source/transforms.rst`.
6. Add **paired tests** `tests/transforms/test_foo.py` and `test_food.py`.
7. Run `./runtests.sh --autofix`, then `./runtests.sh -f -u --quick`, until green.

## Commands (verified against `runtests.sh`)

| Command | What it does |
|---|---|
| `./runtests.sh --autofix` | auto-fix **isort + black + ruff** and copyright headers |
| `./runtests.sh --ruff` | ruff lint check |
| `./runtests.sh --mypy` | mypy static type check |
| `./runtests.sh -f -u --quick` | format/static checks (`-f` = isort+black+ruff+copyright) + quick unit tests |
| `./runtests.sh -f -u --net --coverage` | **PR-recommended** full run |

`-f` does **not** run mypy/pytype — run `--mypy` (and `--pytype`) separately.

## Conventions

- Apache-2.0 copyright header (10 lines) on **every** file; `from __future__ import annotations`
  as the first import.
- **Full type hints**: `NdarrayOrTensor` for image in/out, `KeysCollection` for `keys`,
  `dict[Hashable, NdarrayOrTensor]` for dictionary `__call__` returns.
- **Google-style docstrings** with an `Args:` block; the dictionary class cross-references the array
  class via `:py:class:`.
- Naming: **PascalCase** classes, **snake_case** modules/tests; dictionary class = array name + `d`.
- The **lint + mypy/pytype gate is authoritative** — if it disagrees with this doc, the gate wins.

## Operating rules (for agents)

- **Ground in a reference pair** before writing; never invent a convention.
- **Ask before assuming.** If a task is ambiguous or needs out-of-scope files, stop and ask.
- **Stay in boundaries** (see the read-only list and `.cursor/rules/agent-boundaries.mdc`). In
  Cursor these are **hook-enforced** — `.cursor/hooks.json` hard-blocks edits to protected paths and
  gate-crossing commands (see `LIFECYCLE.md` → Enforcement).
- **Be honest about unknowns** — state what you couldn't verify and how to check it
  (e.g. "couldn't run `--mypy` in this environment; run it to confirm types").
