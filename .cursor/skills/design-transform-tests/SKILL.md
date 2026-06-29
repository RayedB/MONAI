---
name: design-transform-tests
description: "Design (never implement) the test plan for a requested MONAI transform. Use when a GitHub issue is labeled stage:test-design, or when asked to design tests for a transform request. Reads the issue intent, names and mirrors the closest existing transform pair's tests, proposes review-ready scenarios for a human, posts them on the issue, and advances it to stage:test-review. Read-only on code: writes no transform code and opens no PR."
---

# design-transform-tests

Turn a transform **request** (intent captured by `/request-transform`) into a **test plan a human can
approve** — before any code is written. You design tests; engineering implements them later, behind
the `stage:test-review` gate (see `LIFECYCLE.md` at the repo root).

## Boundaries (non-negotiable)
- **Read-only on code.** You may *read* `monai/` and `tests/` to find a reference; you write **no**
  transform code and open **no** PR. Obey `.cursor/rules/agent-boundaries.mdc`.
- **Only ever move work _into_ review.** Your single state change is
  `stage:test-design → stage:test-review`. A human owns the gate after that.
- **Be honest about coverage and assumptions.** You are *proposing* tests from the stated intent, not
  verifying behaviour. Never imply you confirmed a numerical result. Anything uncertain is an explicit
  assumption or an open question. **Especially: never invent the exact math** if the request was vague
  — surface it for confirmation.

## Step 1 — Read the request
From the issue body, extract: **what** it should do to an image, **why** (augmentation vs
preprocessing), the **suspected category** (intensity / spatial / crop-pad / post / *to confirm*), and
whether it is **deterministic or random**. Carry forward every "to confirm by engineering" note.

## Step 2 — Name the reference pair to mirror
Per `.cursor/rules/monai-testing.mdc`, find and **name** the closest existing transform **pair** and
its test file(s), then mirror their structure. Choose by category + behaviour, e.g.:
- intensity → `monai/transforms/intensity/{array,dictionary}.py`; tests
  `tests/transforms/test_shift_intensity.py` + `test_shift_intensityd.py`
- spatial / crop-pad / post → the nearest pair in that category.

State the choice explicitly — e.g. *"Mirroring `ShiftIntensity` / `ShiftIntensityd` and
`test_shift_intensity{,d}.py`"* — so the reviewer can sanity-check the analogy.

## Step 3 — Design scenarios
Group by what actually matters for a MONAI transform. For **each** scenario give a one-line **intent**
and **what it asserts**. Always include the first five groups; include **Randomness** only for a
`RandomizableTransform`.

| Group | Design it to assert |
|---|---|
| **Correctness** | Core behaviour on a small known input gives the expected output. **State the expected math in plain terms** (e.g. `out = max - in` for an inversion). If the request didn't pin the math down, mark it an assumption + open question — never guess silently. |
| **Array/dict parity** | The dictionary version on a key equals the array version applied to that same image. |
| **Cross-backend agreement** | Identical results for a Torch tensor and a NumPy array input (the `backend` attribute promises this); assert via `assert_allclose(..., type_test="tensor")` looping over `TEST_NDARRAYS`. |
| **Numerical / dtype edges** | Value overflow/underflow & safe-casting, negative values, zeros, float-vs-int dtypes, and value-range boundaries — dtype preserved where promised. |
| **Shape / channel handling** | 2D and 3D inputs, channel-first layout; for the dict version also `allow_missing_keys` and multiple keys. |
| **Randomness** *(only if `RandomizableTransform`)* | Reproducibility under a fixed seed; `set_random_state` / the `randomize` flow behaves; output stays within the declared bounds (test the *range*, not one fixed value). |

## Step 4 — Write the review comment
Produce a single Markdown comment in this shape:

```markdown
## 🔴 Test design — needs human review

**Reference mirrored:** `<Array>` / `<Array>d` — `tests/transforms/test_<x>.py` (+ `*d`)

### Assumptions (to confirm by engineering)
- e.g. "Expected math assumed `out = max - in`; the request said only 'flip brightness' — confirm."
- carry over every "to confirm" from the request (suspected category, per-channel vs whole-image, …)

### Proposed test scenarios
| Group | Scenario (intent) | What it asserts |
|---|---|---|
| Correctness | … | … |
| Array/dict parity | … | … |
| Cross-backend | … | … |
| Numerical/dtype edges | … | … |
| Shape/channel | … | … |
| Randomness | … | …  ← omit row if deterministic |

### Open questions for the requester / QA
- e.g. "Clip or wrap on overflow?"
- e.g. "Apply per-channel or to the whole image?"
```

## Step 5 — Post and advance (your only state change)
```
gh issue comment <n> --body "<the markdown above>"
gh issue edit <n> --add-label "stage:test-review" --remove-label "stage:test-design"
```
Moving to `stage:test-review` **is** the review request — a human picks it up via `/approve-tests`.
Do **not** write transform code or open a PR here.

> Requires `gh` with **push access** (the `RayedB` account in this environment;
> `gh auth switch --user RayedB` if a write returns `HTTP 404`).

---

### Authoring note (format confirmed)
Verified against current docs — Cursor added **Agent Skills in v2.4 (Jan 2026)**: skills live at
`.cursor/skills/<name>/SKILL.md` (the folder name must equal `name`), require `name` + `description`,
and the agent **auto-surfaces** a skill from its `description` (or you invoke it with `/`). Source:
`cursor.com/docs/skills`. Because this is the open Agent Skills standard (also discovered from
`.claude/skills/` and `.codex/skills/`), **this file's body works verbatim as a cloud-automation
prompt** — paste it as the automation's instructions.
