---
name: darshan-singh-meel-code
description: Coding discipline for minimal, correct, secure, efficient changes with no AI slop. Use when writing, editing, debugging, or refactoring code — Python, SQL, dbt, Snowflake, Databricks/PySpark, Airflow, ADF, Terraform, or anything else.
---

# Code
Guards against: overbuilt code, bloated abstractions, side-edits, silent assumptions, false "done". CLAUDE.md applies. Data work → also `darshan-singh-meel-data-platform` (only refs for tools in use).

## Before
- Read the code, its callers/downstream models, tests. Reuse project patterns (helpers, macros, operators, logging, tests).
- Restate task in 1–2 lines. Data work → state grain + expected rows/shape.
- Risky assumption or ambiguity → ask. Unclear requirements · many files · schema/interface change · several approaches → `darshan-singh-meel-ask-me` first. Clear/trivial → just do it.
- Graph exists → read its `index.md`.

## Write
- Smallest correct change. 5 lines over 50. Finish: "can I delete any of this?" → delete.
- Edit a line > add a function > add a file/model.
- No speculative options, flags, future-proofing. Abstract only at 3 real uses. Stdlib over new dependency.
- Touch only needed lines. No reformat, rename, reorder, "improve" nearby code. Match existing style.
- Don't delete what you don't understand → flag it. Public interface change (signature, API, table/column, schema, DAG/task id) → only if required, call it out.
- Remove your own debug code, temp files, dead code. Unrelated issues → mention, don't fix.

## Correct · secure · fast
- Edge cases: empty, NULL, zero, duplicates, boundaries, timezones, late data.
- Root cause, not symptom. Reproduce first; cause in one line. No try/except, null check, retry, `DISTINCT`, sleep to hide errors.
- Release resources on every path. Data writes and jobs idempotent.
- No hardcoded secrets. No string-built SQL/shell/paths from input → parameters. Validate input at entry. No unsafe deserialization. Least privilege. No PII/secrets in logs.
- Destructive or irreversible (drop/replace table, delete data/files, force-push, prod `--full-refresh`) → ask first.
- Right data structure; no N+1; push heavy work to the engine; filter/select early. No premature optimisation.

## No slop
- No single-use wrappers, managers, factories, interfaces.
- No checks for impossible cases; no try/except around safe code; no unasked logging/prints/boilerplate.
- Comments: why only; never addressed to the user. No placeholders, TODOs, commented-out code, unused params, unasked READMEs.

## Tests
- Fewest tests, most behaviour: main path · likeliest edge · error path, ideally one parametrised test. Bug fix → one regression test (fails before, passes after).
- Behaviour, not internals. Don't test framework/library. Mock only slow/external.
- Never weaken, skip, delete tests or special-case code to pass. Test seems wrong → say so.
- Data work → data-platform `references/testing.md`.

## Verify · report
- Data checks → `darshan-singh-meel-notebook` (cells only; DDL/DML/dbt run → user's changes notebook).
- State success check up front (test, command, query, row count). 
- Tests: 1. changed code only — tests for changed files/functions (graph `illustrates`, else name/import), `pytest <files>`/`-k`, `dbt build --select state:modified+`, changed DAG import, `terraform validate`/`plan`; lint + types on changed files. 2. Always ask once: "Run the full suite in the background?" Yes (rec) · No · Always this session → background job, keep working, one line when done (failures `file:line`). 3. Report changed-only vs full, and what didn't run.
- Larger tasks: small working steps; check in on scope change, new dependency, many files; plan stops making sense → stop, say so.
- Relax for: trivial edits · labelled throwaway scripts (still no hidden errors or secrets) · explicit refactor requests (surgical rule = requested scope).
- Summary: **Changed** (one line each) · **Why** (one line) · **Verified** · **Not verified / risks** · Other findings (optional).
- Graph exists → end with the one-line `"go"` / `"graph"` / `"no"` offer.
