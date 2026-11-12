---
name: darshan-singh-meel-review
description: Thorough code review for correctness, security, performance, design, complexity, verbosity, AI slop, tech debt, unused files, and cross-repo impact — including SQL, dbt, Snowflake, Databricks/PySpark, Airflow, ADF, Terraform, and Python. Use when asked to review a diff, PR, commit, file, model, DAG, or codebase — "review this", "check my changes", "before I commit", "is this overengineered", "is this secure/fast".
---

# Review
Check everything; report only what matters. CLAUDE.md applies. Data work → also `darshan-singh-meel-data-platform` (refs for tools in the diff only) → §10.

## 0. Setup — one prompt
- Size: change = diff · PR · commit of any size, or ≤20 named files. Large = whole repo · folder · >20 named files.
- Always: "Also look for files the repo doesn't need?" Yes (rec) · No. · "Run the full test suite in the background?" Yes (rec) · No · Always this session.
- Large only:
  - Graph exists → Update first, then review (rec) · Use as is (no update) · Ignore graph (code only). None → Build first (rec) · Code only. Runs on Opus; review starts after. Record: graph `update.py --choice now` (update) · `--choice skip` (as is) → no repeat graph question.
  - Related repos saved → "Include related repos?" Yes (rec) · No.
- Change → no setup graph question, no waiting.

## Steps
1. Goal of the change (PR text, commit, or ask) → review against it.
2. Read the diff + callers, callees, tests, data in/out. Graph (`<repo>-knowledge-graph/` or `./.knowledge-graph` pointer) exists → use as map, never as truth:
   - Impact: walk edges from each changed function/model/table/task/config → check those places in code.
   - Data model: vs `data/model.json` → broken key, changed grain, unknown table/column.
   - Rules and flows that cover it → flag changed behaviour. High-priority docs → flag drift from them.
   - Graph `possible_issue` notes (not verified) for files in scope → check each: confirm as finding with fix, or rule out.
   - System graph (`_combined`, no question) → cross-repo callers of changed routes, contracts, procedures, tables, topics, schemas (`repo:path:line`) → Must/Should fix.
   - Stale graph for these files → read code. No graph → search code.
3. Tests per `darshan-singh-meel-code` (changed-code tests first; full suite per step 0 answer) + lint, types, security on changed files. Say changed-only vs full.
4. Go through every section below (skip only if truly n/a; §11 only if Yes in step 0; §12 always).
5. End (change review): graph stale → graph update question or staleness note, per `update.py --dry-run` (knowledge-graph "Keep it updated"). Else silent on graph.

## 1. Correctness
Trace main path by hand · edges (empty, NULL, zero, negative, off-by-one, duplicates, unicode, huge) · errors surfaced, never swallowed · root cause vs hidden symptom · races, shared state, check-then-act · resources released on every path · types, units, overflow, floats, timezones, encodings · breaking interface/schema changes called out.

## 2. Security
Injection (SQL, shell, eval, templates, paths, regex, HTML) · secrets in code, logs, URLs, config · missing/bypassable auth, IDOR · client-side-only checks · unvalidated input sizes/types/ranges, trusted headers/filenames · path traversal, unsafe temp files, broad permissions, unsafe deserialization · XSS, CSRF, open redirect, SSRF, CORS, missing security headers · homemade crypto, weak hashing, weak randomness · PII in logs/errors · risky new dependencies · destructive ops without safeguard.

## 3. Performance (realistic scale only)
O(n²) where O(n) is easy, repeated searches that should be set/dict lookups · N+1 / calls in loops, missing batching · missing index, unbounded queries (no limit/pagination) · repeated work · whole files in memory · blocking I/O in async/hot paths · unbounded caches, listeners never removed · big copies, string concat in big loops. No speculative caching or parallelism.

## 4. Design
Fits existing patterns (no second way) · logic in the right layer · clear responsibilities · hidden coupling, global state · duplication (but no abstraction for 2 copies) · misleading names · right types (enums vs strings) · APIs hard to misuse.

## 5. Complexity
Junior can follow in one read? · nesting ≥3 → guard clauses · long functions → split only where it helps · clever one-liners, dense comprehensions, metaprogramming → plain code · frameworks, plugin systems, config for one use · wrapper chains, one-impl interfaces → inline. Show the simpler version.

## 6. Size
Same result with much less code? → show it · existing helper/stdlib does it · speculative options → remove · dead code, unused imports → remove · dependency for a few lines · out-of-scope edits → revert/split.

## 7. Slop
Comments restating code · impossible-case checks, needless try/except, redundant type checks · excessive logging · bloated names, messages, boilerplate · TODOs, placeholders, "example usage" blocks, commented-out code · unasked docs · copy-pasted blocks.
- Chat leakage (comments · docstrings · commit/PR messages · docs · generated reports · UI copy addressed to the requester or recalling the chat: "as requested" · "per user" · "as discussed" · "Claude added" · "you haven't confirmed this on prod") → Should; misstates facts or exposes private chat → Must. Fix: fact about the system ("Not yet tested in production").

## 8. Tests
Tested? Regression test for bug fixes? · suggest only the 1–3 most valuable missing tests (main path, likeliest edge, error path, security input) · near-duplicates → one parametrised · framework tests → remove · internals → behaviour · over-mocking → mock only slow/external things · flaky (time, sleep, unseeded random, order, network) · **red flag:** weakened, skipped, deleted, special-cased.

## 9. Obvious
Typos · debug leftovers, local paths, localhost, test credentials · wrong returns, unreachable code, inverted conditions · copy-paste slips · missing `await`, mutable defaults, `==` vs `is` · env changes that break other envs · magic numbers.

## 10. Data stack (if in the diff)
Grain correct, join fan-out, `DISTINCT` hiding bad joins · NULL traps (`NOT IN`, `LEFT JOIN`+`WHERE`, `COUNT(col)`) · deterministic `QUALIFY ROW_NUMBER()` · idempotent reruns, late data, matches `--full-refresh` · dbt: `ref`/`source`, layer, PK `unique`+`not_null`, materialization, no one-off macros · Snowflake: prunable filters, no `SELECT *` on wide tables, no admin roles, risky `CREATE OR REPLACE` · Spark: no `collect`/`toPandas`/row loops, built-ins over UDFs, partitioning, idempotent Delta · Airflow: no `datetime.now()` in task logic or `start_date`, no heavy top-level code or `Variable.get()` at parse time, no big XCom, sensor timeout/reschedule, Connections · ADF: parameterised, managed identity/Key Vault, one window per run, retries + alerts, deployed from CI · versions: only pinned-version features, no deprecated syntax · Python: no f-string SQL from external input, vectorised, push to warehouse · RBAC: roles/groups not users, least privilege, no admin roles in pipelines, service identity per pipeline, grants as code · Terraform: unexpected replace/destroy, `prevent_destroy`, pinned versions, no secrets in `.tf`, committed `*.tfvars` flagged by path, state per env · storage: private, encrypted, identity not keys, prefix layout, lifecycle · cost: scans/compute far beyond need · tests per data-platform `testing.md`: PK + riskiest rule, not every column. Tag `[Data]` or more specific.

## 11. Unused files (only if Yes in step 0)
Never delete, move, or edit — only list.
- Look for: code nothing imports/calls/refs (modules, SQL, macros, unexposed dbt models, unloaded DAGs, unused notebooks) · leftovers (`*_old`, `*_v1`, `*_backup`, `copy of …`, `.bak`, tmp, scratch, commented-out-only files) · stale/duplicate/empty `.md` · config, data, assets nothing reads.
- How: graph (no incoming imports/calls/ref/reads/documents edges) is best; else search names, module paths, table/model names.
- Never unused: entry points, tests, CI/deploy, migrations, IaC, README, LICENSE, CLAUDE.md, .gitignore, package/lock files, pattern/dynamically loaded files, generated/git-ignored outputs (`*-knowledge-graph/`, docs tagged `darshan-singh-meel-docs`, `reviews/`, `analysis/`). Unsure → **Check**.
- Table: `File | Why unused | Evidence | Confidence | Suggestion` + one line on impact (what removing saves, what keeping costs). Confidence: High (no refs, clearly old) · Medium (no refs, maybe dynamic) · Check (owner confirms). User decides.

## 12. Tech debt (always)
Hacks, workarounds · duplicated logic · outdated/unpinned/EOL versions, deprecated APIs · untested risky code · hard-coded config/env values · dead or legacy paths kept alive · TODO/FIXME debt · manual steps to automate · schema/contract drift. Each `[Tech debt]`: what · cost of keeping (time, risk, money) · fix · effort S/M/L. Bugs/security/data risk → Must; growing cost → Should; else Other. Real debt only.

## Discipline
- Committed secret file → flag by path only, never open or quote; scripts, grep, scanners too: exclude those patterns, report path + rule name, value `<redacted>`.
- Every finding: `file:line` — what · why · smallest fix (snippet if short).
- Don't invent problems; fine → don't mention. Unsure → Questions. No praise, no code summary, no generic advice. Match project conventions. Report may address the reader; never quotes the chat.
- Must fix: bugs, security, data loss (incl. debt causing them), broken/gamed tests, unintended breaking changes, serious performance.
- Should fix: design, growing-cost tech debt, needless complexity/code, out-of-scope edits, slop, missing key test, moderate performance.
- Other findings (optional; CLAUDE.md format: what · why · impact): lower-impact only; real risk → Must/Should.

## Output (terminal + `reviews/review-YYYY-MM-DD-HHMM.html`)
```
Verdict: Approve | Approve with changes | Request changes
Checks run: tests → result, linter → result | not run (why)
Tech debt: N items, biggest: <what> | none found

Must fix
- [Security] path/file.py:42 — <problem>. <why>. Fix: <fix>
Should fix
- [Complexity] path/file.py:88-120 — <problem>. Fix: <simpler version>
- [Tech debt] path/file.py:8 — <what>. Cost: <…>. Fix: <fix>. Effort: S|M|L
Questions
Unused files (table, §11)
Areas checked with no issues: <…>
Net size: <e.g. could drop ~40 of 65 added lines>
Other findings (only if any)
```
- Tags: Correctness · Security · Performance · Design · Complexity · Size · Slop · Tests · Obvious · Data · Tech debt. Omit empty sections. No findings → verdict, checks, "No issues found."
- HTML: same content, style per docs skill `references/html-style.md`, self-contained, works without JS. Give the path.
- `reviews/` git-ignored per CLAUDE.md. Commit only if asked (then remove the `/reviews/` line, say so). Already tracked → tell user once: `git rm -r --cached reviews/` (don't run unasked).
