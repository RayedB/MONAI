# /scaffold-transform — generate a new MONAI transform pair (guided)

Scaffold a complete, **green** transform contribution: the array + dictionary pair, registration,
paired tests, and a passing verification run. Runs at `stage:scaffold` (see `LIFECYCLE.md`). Drive
every decision from the project rules and **name them as you go**: `monai-transform-pattern`,
`monai-conventions`, `monai-testing`, `agent-boundaries`.

## Constraints (read first)
- **Stay in boundaries** (`agent-boundaries.mdc`). Create/modify ONLY: `monai/transforms/<category>/array.py`,
  `…/dictionary.py`, `monai/transforms/__init__.py` (registration only), `docs/source/transforms.rst`
  (one entry), and the two test files. `.cursor/hooks.json` enforces this — anything else is hard-blocked.
- **No external code** — mirror existing MONAI patterns only.
- **Ask, don't assume** (Step 0). **Never finish red** — lint, types, and tests must all pass (Step 4).

## Step 0 — Gather inputs (ASK if any are missing)
If anything below is unspecified, **stop and ask** before generating anything:
- **Name** — PascalCase (e.g. `GammaCorrection`); the dictionary version is the name + `d`.
- **Category** — `intensity` / `spatial` / `croppad` / `post` / `utility` / …
- **Determinism** — deterministic (`Transform`) or random (`RandomizableTransform`).
- **Operation** — the semantics in one line (e.g. `out = max - in`).
- **Array constructor parameters** — names + types (e.g. `gamma: float`, `safe: bool = False`).

## Step 1 — Name the reference pair (mirror, don't invent)
Find and **name** the closest existing pair — matching **determinism** and **shape behaviour** — and
say *why* (`monai-transform-pattern`, `monai-testing`). E.g. *"Mirroring `ShiftIntensity` /
`ShiftIntensityd` — deterministic, whole-image intensity, same `backend`."* Read that pair **and** its
test file(s) before writing anything.

## Step 2 — Generate (respecting `agent-boundaries`)

**Array class → `monai/transforms/<category>/array.py`** (`monai-conventions` + `monai-transform-pattern`):
```python
class Name(Transform):  # RandomizableTransform if random
    """<one-line summary>.

    Args:
        <param>: <description>.
    """

    backend = [TransformBackends.TORCH, TransformBackends.NUMPY]

    def __init__(self, <params>) -> None:
        ...

    def __call__(self, img: NdarrayOrTensor) -> NdarrayOrTensor:
        img = convert_to_tensor(img, track_meta=get_track_meta())
        ...
        return out
```
Add `"Name"` to that file's `__all__`. The Apache header, `from __future__ import annotations`, and
the imports above already exist in the file — **reuse them, don't re-add**.

**Dict wrapper → `monai/transforms/<category>/dictionary.py`** (`monai-transform-pattern`):
```python
class Named(MapTransform):
    """Dictionary-based wrapper of :py:class:`monai.transforms.Name`.

    Args:
        keys: keys of the corresponding items to be transformed.
        <param>: <description>.
        allow_missing_keys: don't raise exception if key is missing.
    """

    backend = Name.backend

    def __init__(self, keys: KeysCollection, <params>, allow_missing_keys: bool = False) -> None:
        super().__init__(keys, allow_missing_keys)
        self.<xform> = Name(<params>)  # descriptive attribute name

    def __call__(self, data: Mapping[Hashable, NdarrayOrTensor]) -> dict[Hashable, NdarrayOrTensor]:
        d = dict(data)
        for key in self.key_iterator(d):
            d[key] = self.<xform>(d[key])
        return d
```
Import `Name` into the `from monai.transforms.<category>.array import (...)` block; add `"Named"` and
`"NameDict"` to `__all__`; and add the **triple alias** at the file bottom:
```python
NameD = NameDict = Named
```

**Register** (`monai-transform-pattern`):
- `monai/transforms/__init__.py` — add `Name` to the `.<category>.array` import block and
  `Named, NameD, NameDict` to the `.<category>.dictionary` block (keep alphabetical — isort enforces).
- `docs/source/transforms.rst` — add `.. autoclass:: Name` in the category section and
  `.. autoclass:: Named` under **Dictionary Transforms**, mirroring neighbours (omit the external
  `.. image::` line for a brand-new transform).

## Step 3 — Paired tests (`monai-testing`)
Create `tests/transforms/test_<snake>.py` and `tests/transforms/test_<snake>d.py`, mirroring the
reference test:
- Apache header + `from __future__ import annotations`; import from the **public API**
  (`from monai.transforms import Name, Named`) — this also proves registration.
- `unittest` (+ `parameterized` with `TEST_CASE_*` where the reference uses it).
- **Cross-backend**: loop `for p in TEST_NDARRAYS:` and assert
  `assert_allclose(result, p(expected), type_test="tensor")`.
- **One numerical / dtype edge** (e.g. overflow / clipping, dtype preserved, zeros / negatives).

## Step 4 — Verify (never finish red)
Run the **scoped verifier** — it formats/lints only the files you touched (repo pins), checks both
docs registrations, and runs the paired tests (~1 min). **Show its output**, fix until green:
```bash
./.cursor/scripts/verify-transform.sh <snake> <category>
```
The **full** repo gates (isort/black/ruff/**mypy** over everything + the suites) run in CI on the
PR and are authoritative — do **not** run repo-wide `./runtests.sh --autofix` from a scaffold: it
reformats unrelated files and pollutes the PR. (Working locally with time to spare?
`./runtests.sh --ruff --mypy` before pushing catches type errors earlier.)

## Step 5 — Report
- **Files created / modified** — list all, including `monai/transforms/__init__.py` and
  `docs/source/transforms.rst`.
- **Reference pair mirrored** — name it.
- **Which rule drove each key decision** — name them: `monai-transform-pattern` (pair + triple alias +
  registration), `monai-conventions` (header / types / naming / docstring), `monai-testing`
  (cross-backend + edge case), `agent-boundaries` (which files you touched).
- **Verification results** — lint / mypy / test output, all green.
- **Uncertainties + how to verify** — e.g. "assumed clip-on-overflow; confirm with QA, or run
  `./runtests.sh --pytype`."

## Next (lifecycle)
With everything green, open a PR (`gh pr create`) to move the issue to `stage:in-review` for human
review. **Never merge** — that's a human gate (the shell-guard hook blocks it anyway).

## Running in the cloud (this stage's native surface)
Scaffold runs as a **Cursor automation** (dashboard-configured cloud agent) whose instructions
point at this file — the approval *is* the dispatch, synchronously: `/approve-tests` swaps the
label **and POSTs the automation's private webhook from the approver's machine** (instant; no CI
queue; credentials live in the approver's local environment). Fallbacks, in order:
`gh workflow run scaffold-agent.yml -f issue=<n>` (the
[Actions relay](../../.github/workflows/scaffold-agent.yml), same webhook via repo secrets — may
queue), or run the automation by hand from cursor.com/automations. The VM installs the dev environment via
[.cursor/environment.json](../environment.json); the repo rules **and** the guard hooks bind the
agent in the cloud too. **Label fallback:** the cloud agent's minted token cannot edit issue labels
(no `issues: write` — same platform gap as triage). If the `stage:scaffold → stage:in-review` swap
fails, say so in the PR body; the human reviewer applies the label at the gate they own.
