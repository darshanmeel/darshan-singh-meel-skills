---
name: darshan-singh-meel-review
description: Thorough code review for correctness, security, performance, design, complexity, verbosity, AI slop, unused files, and cross-repo impact — including SQL, dbt, Snowflake, Databricks/PySpark, Airflow, ADF, Terraform, and Python. Use when asked to review a diff, PR, commit, file, model, DAG, or codebase — "review this", "check my changes", "before I commit", "is this overengineered", "is this secure/fast".
---

# Review
Check everything; report only what matters. CLAUDE.md applies. Data work → also `darshan-singh-meel-data-platform`.

## 0. Setup — one prompt
- Size: change = diff · PR · commit · ≤20 files. Large = whole repo · >20 files.
- Always: "Also look for files the repo doesn't need?" Yes (rec) · No.
- Large only:
  - Graph exists → Update first, then review (rec) · Use as is · Skip. None → Build first (rec) · Code only. Runs on Opus; review starts after.
  - Related repos saved → "Include related repos?" Yes (rec) · No.
- Change → no graph question, no waiting.

## Steps
1. Goal of the change (PR text, commit, or ask) → review against it.
2. Read the diff + callers, callees, tests, data in/out. Graph exists → use as map, never as truth:
   - Impact: walk edges from each changed function/model/table/task/config → check those places in code.
   - Data model: vs `data/model.json` → broken key, changed grain, unknown table/column.
   - Rules and flows that cover it → flag changed behaviour. High-priority docs → flag drift from them.
   - Graph `possible_issue` notes (not verified) for files in scope → check each: confirm as finding with fix, or rule out.
   - System graph → cross-repo callers of changed routes, contracts, procedures, tables, topics, schemas (`repo:path:line`) → Must/Should fix.
   - Stale graph for these files → read code. No graph → search code.
3. Tests covering the change only (not whole suite) + lint, types, security on changed files. Then ask once: "Full suite in the background?" Yes (rec) · No · Always this session. Say changed-only vs full.
4. Go through every section below (skip only if truly n/a).
5. Real findings only, each with a concrete fix.
6. End (change review): graph stale → one-line `"go"` / `"graph"` / `"no"` offer. No graph and >20 files → suggest one. Else silent on graph.

## 1. Correctness
Trace main path by hand · edges (empty, NULL, zero, negative, off-by-one, duplicates, unicode, huge) · errors surfaced, never swallowed · root cause vs hidden symptom · races, shared state, check-then-act · resources released on every path · types, units, overflow, floats, timezones, encodings · breaking interface/schema changes called out.

## 2. Security
Injection (SQL, shell, eval, templates, paths, regex, HTML) · secrets in code, logs, URLs, config · missing/bypassable auth, IDOR · unvalidated input sizes/types · path traversal, unsafe temp files, broad permissions, unsafe deserialization · XSS, CSRF, open redirect, SSRF, CORS · homemade crypto, weak hashing, weak randomness · PII in logs/errors · risky new dependencies · destructive ops without safeguard. Committed secret file → flag by path only, never open or quote.

## 3. Performance (realistic scale only)
O(n²) where O(n) is easy · N+1 / calls in loops · missing index, unbounded queries · repeated work · whole files in memory · blocking I/O in async/hot paths · unbounded caches, leaks · big copies. No speculative caching or parallelism.

## 4. Design
Fits existing patterns (no second way) · logic in the right layer · clear responsibilities · hidden coupling, global state · duplication (but no abstraction for 2 copies) · misleading names · right types (enums vs strings) · APIs hard to misuse.

## 5. Complexity
Junior can follow in one read? · nesting ≥3 → guard clauses · split only where it helps · clever one-liners, metaprogramming → plain code · frameworks/config for one use · wrapper chains, one-impl interfaces → inline. Show the simpler version.

## 6. Size
Same result with much less code? → show it · existing helper/stdlib does it · speculative options → remove · dead code, unused imports → remove · dependency for a few lines · out-of-scope edits → revert/split.

## 7. Slop
Comments restating code or addressing the user · impossible-case checks, needless try/except · excessive logging · bloated names, messages, boilerplate · TODOs, placeholders, commented-out code · unasked docs, debug leftovers · copy-pasted blocks.

## 8. Tests
Tested? Regression test for bug fixes? · suggest only the 1–3 most valuable missing tests · near-duplicates → one parametrised · framework tests → remove · internals → behaviour · over-mocking · flaky (time, sleep, unseeded random, order, network) · **red flag:** weakened, skipped, deleted, special-cased.

## 9. Obvious
Typos · debug leftovers, local paths, localhost, test credentials · wrong returns, unreachable code, inverted conditions · copy-paste slips · missing `await`, unclosed resources, mutable defaults, `==` vs `is` · env changes that break other envs · magic numbers.

## 10. Data stack
Grain correct, join fan-out, `DISTINCT` hiding bad joins · NULL traps (`NOT IN`, `LEFT JOIN`+`WHERE`, `COUNT(col)`) · deterministic `QUALIFY ROW_NUMBER()` · idempotent reruns, late data, matches `--full-refresh` · dbt: `ref`/`source`, layer, PK tests, materialization, no one-off macros · Snowflake: prunable filters, no `SELECT *` on wide tables, no admin roles, risky `CREATE OR REPLACE` · Spark: no `collect`/`toPandas`/row loops, built-ins over UDFs, partitioning, idempotent Delta · Airflow: no `datetime.now()`, no parse-time work, no big XCom, sensor timeouts, Connections · ADF: parameterised, managed identity/Key Vault, one window per run, retries + alerts, deployed from CI · Python: no f-string SQL, vectorised, push to warehouse · RBAC: roles/groups not users, least privilege, grants as code · Terraform: unexpected replace/destroy, `prevent_destroy`, pinned versions, no secrets, state per env · storage: private, encrypted, identity not keys, lifecycle · versions: only pinned-version features, no deprecated syntax · cost: scans/compute far beyond need · tests per data-platform `testing.md`. Tag `[Data]` or more specific.

## 11. Unused files (asked every review)
Never delete, move, or edit — only list.
- Look for: code nothing imports/calls/refs (modules, SQL, macros, unexposed dbt models, unloaded DAGs, unused notebooks) · leftovers (`*_old`, `*_v1`, `*_backup`, `.bak`, tmp, scratch) · stale/duplicate/empty `.md` · config, data, assets nothing reads.
- How: graph (no incoming imports/calls/ref/reads/documents edges) is best; else search names, module paths, table/model names.
- Never unused: entry points, tests, CI/deploy, migrations, IaC, README, LICENSE, CLAUDE.md, .gitignore, package/lock files, pattern/dynamically loaded files, generated outputs (`*-knowledge-graph/`, tagged docs). Unsure → **Check**.
- Table: `File | Why unused | Evidence | Confidence (High · Medium · Check) | Suggestion` + one line on impact. User decides.

## Discipline
- Thorough checking, brief reporting. Every finding: `file:line` — what · why · smallest fix (snippet if short).
- Don't invent problems; fine → don't mention. Unsure → Questions. No praise, no code summary, no generic advice. Match project conventions.
- Must fix: bugs, security, data loss, broken/gamed tests, unintended breaking changes, serious performance.
- Should fix: design, needless complexity/code, out-of-scope edits, slop, missing key test, moderate performance.
- Other findings (optional): lower-impact only; real risk → Must/Should.

## Output (terminal + `reviews/review-YYYY-MM-DD-HHMM.html`)
```
Verdict: Approve | Approve with changes | Request changes
Checks run: tests → result, linter → result | not run (why)

Must fix
- [Security] path/file.py:42 — <problem>. <why>. Fix: <fix>
Should fix
- [Complexity] path/file.py:88-120 — <problem>. Fix: <simpler version>
Questions
Unused files (table)
Areas checked with no issues: <…>
Net size: <e.g. could drop ~40 of 65 added lines>
Other findings (only if any)
```
- Tags: Correctness · Security · Performance · Design · Complexity · Size · Slop · Tests · Obvious · Data. Omit empty sections. No findings → verdict, checks, "No issues found."
- HTML: same content, docs-skill style, self-contained, works without JS. Give the path. Never publish.
- `reviews/` git-ignored by default: before the first report, add `/reviews/` to `.gitignore` (+ one-line comment; create if missing). Commit only if asked (then remove the line, say so). Already tracked → tell user once: `git rm -r --cached reviews/` (don't run unasked).
