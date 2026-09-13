# Repository sprawl audit plan

**Repository:** `agent-config`
**Purpose:** Reduce architectural sprawl and make the repository easier for
agents and humans to understand, without changing the behavior of Claude,
Codex, OMP, Pi, skill delivery, or sandbox bootstrap flows.

This repository is a configuration and tooling system, not a product
application. The audit should therefore focus on ownership, lifecycle,
configuration boundaries, documentation status, and verification—not on
reducing file count for its own sake.

## Operating rules

- Do not delete, merge, or move files merely because they look old or numerous.
- Preserve unrelated dirty work; audit from a clean committed baseline where
  possible.
- Treat `agent-config` and `dotfiles` as separate repositories with explicit
  ownership boundaries.
- Do not apply live configuration, fetch external repositories, rewrite
  credentials, or change model/provider behavior during the audit.
- Separate read-only discovery from implementation.
- Choose one deepening opportunity at a time.
- Every accepted cleanup must have a behavior-preservation check and a rule that
  prevents the same sprawl from returning.

## Phase 0 — establish a baseline

Before the architecture survey:

```bash
git status --short
./scripts/check.sh
```

Record the current branch, relevant commits, and the passing/failing state of
existing checks. Either commit or explicitly exclude unrelated changes. Do not
let an audit branch absorb an existing feature or configuration change.

## Phase 1 — survey the architecture

Run the architecture-health skill first. It should inspect recent history,
current instructions, ADRs, plans, handoffs, configuration, skills, and
verification boundaries, then produce a temporary report without editing the
repository.

### Prompt

```text
/improve-codebase-architecture

Audit this repository as an agent-configuration and tooling system. I want to
reduce architectural sprawl without changing behavior.

Work read-only: do not edit files, delete anything, commit, or modify live
machine configuration. Read the repository instructions, recent history, current
plans, and existing ADRs first. Treat any current uncommitted changes as
out-of-scope unless they reveal a structural issue.

Focus on:

- ownership boundaries between agent-config and dotfiles;
- the skill catalogue, external manifest, ZIPs, and archives;
- duplicated or conflicting Claude, Codex, OMP, and Pi configuration;
- generated, vendored, and tracked artifacts;
- plans, handoffs, TODOs, and verification scripts.

Identify 3–5 concrete deepening opportunities, distinguish real friction from
theoretical cleanup, and recommend one starting point. End by asking me which
candidate I want to explore. Do not propose implementation details yet.
```

Do not ask for a repository-wide cleanup. The output should identify concrete
candidates, explain the locality and leverage each would create, and name a top
recommendation.

## Phase 2 — choose and sharpen one candidate

Pick one candidate from the report. The likely high-value candidates are:

1. skill catalogue and lifecycle;
2. ownership between `agent-config` and `dotfiles`;
3. generated, vendored, and tracked artifact boundaries;
4. cross-harness policy and model-routing duplication;
5. plans, handoffs, decisions, and current-state documentation.

These are hypotheses, not a substitute for the architecture report.

Then run the stateful interview in the working directory. It should create or
update the project glossary and ADRs as decisions become firm.

### Prompt

```text
/grill-with-docs

Use the architecture candidate I selected as the subject of this interview.
Help me define the observable sprawl, the canonical owner for each concern, and
the smallest behavior-preserving change that would deepen the relevant module.

Pressure-test:

- what is actually in scope and what must remain untouched;
- which duplication is accidental versus intentional;
- what can be deleted, consolidated, or merely indexed;
- how Claude, Codex, OMP, Pi, and dotfiles are affected;
- what migration, rollback, and acceptance tests are required;
- what rule or check prevents the sprawl from returning.

Record load-bearing terminology, decisions, and rejected alternatives in the
appropriate CONTEXT.md or ADR files. Do not implement anything until the scope
and acceptance criteria are settled.
```

Do not proceed until the candidate has a clear seam, a bounded outcome, and
observable acceptance criteria.

## Phase 3 — choose the implementation shape

Decide whether the candidate fits in one session.

### Small, one-session change

Use this when the scope is narrow, the files are known, and no unresolved
cross-repository decision remains.

```text
/implement

Implement only the accepted candidate from the architecture interview. Work in
small red-green slices using /tdd, preserve the existing behavior, and run the
narrowest relevant checks after each slice. Finish with /code-review against the
accepted scope before committing. Do not broaden the cleanup into adjacent
sprawl.
```

### Multi-session change

Use this when ownership, verification, catalogue, policy, or documentation work
needs several independently reviewable slices.

```text
/to-spec

Turn the accepted architecture decision into a buildable specification. Include
scope, invariants, current and target ownership, affected harnesses, migration
and rollback behavior, acceptance tests, and explicit non-goals. Keep behavior
changes out of scope unless they were explicitly accepted during grilling.
```

Then:

```text
/to-tickets

Split the specification into tracer-bullet tickets. Each ticket must have one
coherent outcome, explicit blocking edges, named files or surfaces, verification
commands, and a clear out-of-scope list. Order the tickets blockers-first and
keep generated artifacts with their authoritative source change.
```

Implement each ticket in a fresh context:

```text
/implement

Implement this ticket only. Drive the work test-first with /tdd, verify the
specified acceptance criteria, and run /code-review before committing. Stop and
report if the repository contradicts the ticket or if the change would cross an
unapproved ownership or behavior boundary.
```

Use `/wayfinder` instead of `/to-spec` only if the effort is genuinely too large
or uncertain to decompose yet. Use `/diagnosing-bugs` separately for the
prompt-capture crash; do not mix that defect investigation into the sprawl
cleanup.

## Review and verification gate

For each slice, run the narrowest relevant check first, then the repository
suite:

```bash
./scripts/check.sh
git diff --check
git status --short
```

For skill changes, also run:

```bash
python3 scripts/lint-skills.py
python3 scripts/check-zips.py
```

For installer or configuration changes, use disposable homes and preserve the
existing refusal, merge, symlink, and secret-boundary tests. Do not use the real
home directory as a test fixture.

Before committing, run `/code-review` against the fixed point and resolve any
missing requirements or unintended scope. Then use `/commit`. Push only the
resulting reviewed commit with `/push`.

## Completion criteria

The audit is complete when the chosen area has:

- one clear source owner and delivery rule;
- explicit intentional duplication and exceptions;
- a bounded, behavior-preserving implementation;
- tests or checks that detect regression and future drift;
- documentation that distinguishes current truth, decisions, active work, and
  historical material;
- no unrelated files or live machine configuration changed.
