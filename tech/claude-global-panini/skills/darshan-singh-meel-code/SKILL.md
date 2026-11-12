---
name: darshan-singh-meel-code
description: Coding discipline for minimal, correct, secure, efficient changes with no AI slop. Use when writing, editing, debugging, or refactoring code — Python, SQL, dbt, Snowflake, Databricks/PySpark, Airflow, ADF, Terraform, or anything else.
---

# Code
Guards against: overbuilt code, bloated abstractions, side-edits, silent assumptions, false "done". CLAUDE.md applies. Data work → also `darshan-singh-meel-data-platform` (only refs for tools in use).

## Before
- Read the code, its callers/downstream models, tests. Reuse project patterns (helpers, macros, operators, logging, tests).
- Restate task in 1–2 lines. Data work → state grain + expected rows/shape.
- List assumptions; risky assumption or ambiguity → ask. Simplest approach; tradeoff only if it matters. Unclear requirements · many files · schema/interface change · several approaches → `darshan-singh-meel-ask-me` first. Clear/trivial → just do it.
- Graph (folder or `./.knowledge-graph` pointer) exists → read its `index.md`.

## Write
- Smallest correct change. 5 lines over 50. Finish: "can I delete any of this?" → delete.
- Edit a line > add a function > add a file/model.
- No speculative options, flags, future-proofing. Plain functions over new classes/layers; abstract only at 3 real uses. Stdlib over new dependency.
- Touch only needed lines. No reformat, rename, reorder, "improve" nearby code. Match existing style.
- Don't delete what you don't understand → flag it. Public interface change (signature, API, table/column, schema, DAG/task id) → only if required, call it out.
- Remove your own debug code, temp files, dead code. Unrelated issues → mention, don't fix.
- Tech debt touched or found → Other findings: `[Tech debt] what · why it matters · impact of fixing vs not`. Never fix unasked. No trivial items.

## Correct · secure · fast
- Edge cases: empty, NULL, zero, duplicates, boundaries, timezones, late data.
- Root cause, not symptom. Reproduce first; cause in one line. No try/except, null check, retry, `DISTINCT`, sleep to hide errors.
- Release resources on every path. Data writes and jobs idempotent.
- No hardcoded secrets. No string-built SQL/shell/paths from input → parameters/quoting. Validate input at entry. No pickle/`yaml.load` on untrusted data. Least privilege. No PII/secrets in logs.
- Destructive or irreversible (drop/replace table, delete data/files, force-push, `--full-refresh` outside dev) → ask first.
- Right algorithm/data structure; no N+1; push heavy work to the engine; filter/select early; stream/limit over load-all. No premature optimisation, caching, parallelism.

## No slop
- No single-use wrappers, managers, factories, interfaces.
- No checks for impossible cases; no try/except around safe code; no unasked logging/prints/boilerplate.
- Comments · docstrings · commit/PR messages: describe the code, never the chat ("as requested" · "per user" · "as discussed" · "Claude added"); why only. No placeholders, TODOs, commented-out code, unused params, "example usage" blocks, unasked README/docs/summary files.

## Tests
- Fewest tests, most behaviour: main path · likeliest edge · error path, ideally one parametrised test. Bug fix → one regression test (fails before, passes after).
- Behaviour, not internals. Don't test framework/library. Mock only slow/external.
- Never weaken, skip, delete tests or special-case code to pass. Test seems wrong → say so.
- Data work → data-platform `references/testing.md`.

## Verify · report
- Data checks → `darshan-singh-meel-notebook` (cells only; DDL/DML/dbt run → user's changes notebook).
- State success check up front (test, command, query, row count).
- Tests: 1. changed code only — tests for changed files/functions (graph `illustrates`, else name/import), `pytest <files>`/`-k`, `dbt parse` (no connection); `dbt compile --no-introspect --select <changed_model>+` only if needed (`--state <prod-manifest dir>` + `state:modified+` if a manifest exists), import/parse changed DAG file (or project's DagBag test), `terraform validate` (changed modules); lint + types on changed files. plain `dbt compile`/`build`/`test`, `terraform plan` → command or changes notebook for user. 2. Ask once per change, unless "Always this session" chosen (then run without asking): "Run the full suite in the background?" Yes (rec) · No · Always this session; Yes/Always → background job, keep working, one line when done (failures `file:line`). 3. Report changed-only vs full, and what didn't run.
- Report passed · failed · not verified; never "done" when it isn't.

## Larger tasks
- Small working steps; check in on scope change, new dependency, many files; plan stops making sense → stop, say so.

## Relax
- Labelled throwaway scripts (still no hidden errors or secrets) · explicit refactor requests (surgical rule = requested scope).

## Summary
- End of reply, in order: summary · Other findings (+ graph/docs staleness note) · `Skills:` line (last text line); graph/docs question after the reply text.
- Summary: **Changed** (one line each) · **Why** (one line) · **Verified** · **Not verified / risks** · Other findings (optional).
- Graph exists → after commit or task end: graph question or graph/docs staleness note, per `update.py --dry-run` ("Keep it updated" in knowledge-graph skill).
