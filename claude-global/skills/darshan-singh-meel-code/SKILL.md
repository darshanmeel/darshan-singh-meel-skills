---
name: darshan-singh-meel-code
description: Coding discipline for minimal, correct, secure, efficient changes with no AI slop. Use when writing, editing, debugging, or refactoring code — Python, SQL, dbt, Snowflake, Databricks/PySpark, Airflow, or anything else.
---

# Minimal Coding Discipline

Guards against common AI coding failures: overcomplicated code, bloated abstractions, unrequested side-edits, silent assumptions, and unverified "done" claims. Global rules in CLAUDE.md apply.

**Data work:** for SQL, dbt, Snowflake, Databricks/PySpark, Python pipelines, Airflow, Azure Data Factory, Terraform, cloud storage, or RBAC, also follow the `darshan-singh-meel-data-platform` skill (only the reference files for the tools in use).

## 1. Understand before changing
- Read the relevant code first: the function/model, its callers or downstream models, and tests.
- Find how the project already does similar things (helpers, macros, operators, error handling, logging, tests) and reuse that.
- Restate the task in one or two sentences. For data work, state the grain and the expected row count/shape.
- List assumptions. If one is risky or the request is ambiguous, ask instead of guessing.
- Pick the simplest approach that fully solves the problem; mention the tradeoff only if it matters.

**Unsure, or the plan is complicated?** (unclear requirements, many files/models/DAGs, schema or interface changes, several reasonable approaches) → plan it first with `darshan-singh-meel-ask-me`. Trivial or clear tasks: just do them.

## 2. Simplicity first
- Smallest amount of code that correctly solves the problem. If 5 lines work, don't write 50.
- Before finishing, reread the change: "Can I delete any of this and still solve the problem?" If yes, delete it.
- Prefer editing an existing line over adding a function, a function over a new file/module/model.
- No speculative features, options, flags, or "future-proofing."
- Plain functions and existing utilities over new classes, layers, or abstractions. Don't abstract until there are 3 real uses.
- No new dependency when a few lines of standard-library code will do.

## 3. Surgical changes
- Touch only the lines needed. No reformatting, renaming, reordering, or "improving" adjacent code.
- Don't delete or rewrite code you don't understand — flag it.
- Match existing style and patterns, even if you'd do it differently.
- Don't change public interfaces (function signatures, APIs, table/column names, schemas, DAG/task ids) unless required — call it out when you do.
- Remove any debug code, temp files, or dead code *you* added. Mention unrelated problems instead of fixing them.

## 4. Correctness
- Handle realistic edge cases: empty, NULL/None, zero, duplicates, boundaries, timezones, late data.
- Fix root causes, not symptoms. Reproduce the bug first; state the cause in one sentence. No try/except, null checks, retries, `DISTINCT`, or sleeps just to make an error go away.
- Release resources on every path (`with`, try/finally).
- Make data writes and jobs idempotent: rerunning gives the same result.

## 5. Security
- Never hardcode secrets, tokens, or passwords; use the project's config/secrets approach.
- Never build SQL, shell commands, or paths from external input with string formatting; use parameters and proper quoting.
- Validate external input where it enters the system. No unsafe deserialization (pickle, `yaml.load`) of untrusted data.
- Least privilege for roles, service accounts, and permissions. No PII or secrets in logs.
- Ask before anything destructive or hard to undo: dropping/replacing tables, deleting data or files, force-pushing, `--full-refresh` in production.

## 6. Performance
- Choose the right algorithm and data structure (set/dict lookups, not repeated scans).
- No queries or API calls inside loops (N+1); batch instead.
- Push heavy data work to the engine (SQL/dbt/Spark), not into Python.
- Filter and select only needed columns early; don't load everything into memory when streaming/limiting works.
- Don't optimize prematurely or add caching/parallelism without a clear payoff.

## 7. No AI slop
- No wrappers, managers, factories, or interfaces with a single use.
- No defensive checks for impossible cases; no try/except around code that can't fail.
- No unrequested logging, prints, or boilerplate.
- No comments or docstrings that restate the code; comments only explain *why*. No comments addressed to the user.
- No placeholders, TODOs, "example usage" blocks, commented-out code, or unused parameters.
- No new README, docs, or summary files unless asked.
- Short, direct explanations.

## 8. Minimal tests, maximum coverage
- Fewest tests that cover the most behavior. If 100 tests are possible, pick the few that would catch real bugs.
- Usually: main path, the most likely edge case, and the error path — ideally as one parametrized test.
- Bug fix: one regression test that fails before and passes after.
- Test behavior, not internals. Don't test the framework or library. Mock only slow/external things.
- Never weaken, skip, or delete tests, or special-case code to make tests pass. If a test seems wrong, say so.
- For data work, follow `references/testing.md` in the `darshan-singh-meel-data-platform` skill.

## 9. Verify, then report honestly
- Need to check data (row counts, grain, old vs new)? → `darshan-singh-meel-notebook`: checks go in notebook cells; Claude never runs DDL/DML or `dbt run` — those go in the changes notebook for the user.
- State upfront how success will be checked (test, command, query result, row count).
- **Tests — changed code first, full suite on request:**
  1. Run only the tests that cover the change: tests for the changed files/functions (graph `illustrates` edges if a graph exists, else by name/import), `pytest <files>` / `-k`, `dbt build --select state:modified+` (or the changed models `+`), the changed DAG's import test, `terraform validate`/`plan` for changed modules. Plus linter and type checker on changed files.
  2. Then always ask once: "Run the full test suite in the background?" — Yes (Recommended) · No · Always this session. Yes/Always → run it as a background job and keep working; report pass/fail in one line when done (failures with `file:line`).
  3. Report which tests ran (changed-only vs full) and what wasn't run.
- Report what passed, what failed, and what wasn't verified. Don't say "done" when it isn't.

## 10. Knowledge graph
- If `<reponame>-knowledge-graph/` exists (or `./.knowledge-graph` points to one), read its `index.md` first.
- When done, end with the one-line update offer ("go" / "graph" / "no") — see `darshan-singh-meel-knowledge-graph`, section 5.

## 11. Larger tasks
- Small steps, each leaving the code working. Check in when scope changes, a dependency is added, or many files are touched.
- If the plan stops making sense, stop and say so.

## When to relax
- Trivial edits: skip the ceremony and just do it.
- Throwaway scripts/prototypes the user labels as such: favor speed, but never hide errors or hardcode secrets.
- Explicit refactor/cleanup requests: the "surgical" rule applies to the requested scope.

## Final summary
- **Changed:** files/models and what changed, one line each
- **Why:** root cause or reasoning, one sentence
- **Verified:** how it was checked and the result
- **Not verified / risks:** anything untested or uncertain
- **Other findings:** optional, CLAUDE.md format.
