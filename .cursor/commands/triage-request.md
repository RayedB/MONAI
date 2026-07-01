# /triage-request — intake guard for a transform request

Given an issue number `<n>` at `stage:triage`, run the full triage logic defined in the
**[`triage-transform-request`](../skills/triage-transform-request/SKILL.md) skill** — that file is
canonical; follow it exactly. Same logic, two surfaces: this command (a human triager in Cursor)
and CI ([`.github/workflows/triage-agent.yml`](../../.github/workflows/triage-agent.yml), which
auto-fires on new transform requests).

Outcomes, in the order the skill checks them:

1. **Reject — out of scope** (generic PyTorch op / wrong MONAI area) → comment + `out-of-scope` + close *not planned*
2. **Reject — duplicate** (an existing transform already covers it) → comment naming it + `duplicate` + close *not planned*
3. **Hold — needs info** → plain-language questions, stays at `stage:triage`
4. **Advance — clear** → `priority:*` applied, `stage:triage → stage:test-design`, dispatch `test-design-agent.yml`

Notes for the interactive run:
- The deterministic template pre-check (`.github/scripts/check-transform-template.py`) runs
  automatically in CI; interactively, pipe the body through it first —
  `gh issue view <n> --json body -q .body | python3 .github/scripts/check-transform-template.py` —
  and on `ok=false` apply the reject-invalid outcome (comment + `invalid` + close *not planned*,
  inviting a refile via the transform-request form).
- Requires `gh` with push access (the `RayedB` account in this environment;
  `gh auth switch --user RayedB` if a write returns `HTTP 404`).
