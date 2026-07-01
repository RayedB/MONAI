# /triage-request — intake clarity gate

Before engineering spends effort designing tests, make sure a new transform request is **clear enough
to act on**. Given an issue at `stage:triage`, decide: *could engineering write a correctness test from
this?* If yes → advance to `stage:test-design`. If not → post specific, plain-language clarification
questions and hold it in triage for the requester to answer.

This is the **human-run stand-in for the intake automation** — a Cursor cloud automation can't mutate
issues today (its minted token lacks `issues: write`), so a triager runs this; the same logic ships
later as a GitHub Action. See `LIFECYCLE.md`.

## Hard rules
- **Ask, never assume.** If the request is vague, ask — don't fill gaps or guess the behavior/math
  (same principle as `/request-transform`).
- **Plain language.** The requester may be a non-engineer; questions must be answerable without code.
- **Advance only on clarity.** You may move `stage:triage → stage:test-design` (a work step, *not* a
  human gate). Never skip ahead to scaffold/merge.
- **No code edits.** Read the issue; write a comment and/or swap the stage label. Nothing else.

## Steps
1. **Input:** an issue number `<n>` (expected at `stage:triage`).
2. **Fetch:** `gh issue view <n> --comments` — read the request and any author replies.
3. **Assess clarity** — is each of these answerable?
   - **What** should the transform do to an image — a *concrete, testable* operation (not just a goal
     like "make it better")?
   - **Why** — augmentation vs preprocessing / the real use case?
   - **Deterministic or random?** (it changes how the transform is tested)
   - Category and reference are *nice-to-have* — "not sure" is fine (engineering confirms); they do
     **not** block.
   - **The bar:** if the **what** is too vague to assert an expected output, it's not clear enough.

## Decide

**Clear enough → advance + restate:**
```
gh issue edit <n> --remove-label "stage:triage" --add-label "stage:test-design"
gh issue comment <n> --body "✅ Intake clear — moving to test design.
**Understood as:** <one line: what it does · why · deterministic or random>."
```

**Not clear → ask + hold:**
```
gh issue comment <n> --body "Thanks for the request! Before we design tests, a couple of things:
- <specific Q1, e.g. 'By *flip brightness*, do you mean an exact inversion (black↔white), or just brightening dark regions?'>
- <specific Q2, e.g. 'Same every run, or random for augmentation?'>
Reply here and we'll pick it straight back up."
```
Leave it at `stage:triage` (optionally `--add-assignee <requester>` to signal whose turn it is). When
the requester replies, **re-run `/triage-request <n>`**.

> Requires `gh` with push access (the `RayedB` account in this environment).

## Boundary
Triage is an *intake* step, not a review gate — advancing to `stage:test-design` moves work *forward*,
never past a human gate. You ask questions; you never invent the answers.
