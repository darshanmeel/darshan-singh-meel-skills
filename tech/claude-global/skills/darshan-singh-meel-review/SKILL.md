---
name: darshan-singh-meel-review
description: Thorough code review for correctness, security, performance, design, complexity, verbosity, AI slop, tech debt, unused files, and cross-repo impact — including SQL, dbt, Snowflake, Databricks/PySpark, Airflow, ADF, Terraform, and Python. Use when asked to review a diff, PR, commit, file, model, DAG, or codebase — "review this", "check my changes", "before I commit", "is this overengineered", "is this secure/fast".
---

# Thorough Minimal Code Review

Check everything thoroughly; report only what matters. The goal is code that is correct, secure, fast enough, well designed, as small as possible, and free of AI slop. Global rules in CLAUDE.md apply.

**Data work:** for SQL, dbt, Snowflake, Databricks/PySpark, Python pipelines, Airflow, Azure Data Factory, Terraform, cloud storage, or RBAC, also follow the `darshan-singh-meel-data-platform` skill (only the reference files for the tools in the diff) and check the change against it in section 10 (if in the diff).

## How to review
0. **Size the review, then one setup prompt:**
   - **Change review** = a diff, PR, or commit of any size, or up to 20 named files. **Large review** = the whole repo, a folder, or more than 20 named files.
   - **Always:** "Also look for files the repo doesn't need?" — Yes (Recommended) · No. (section 11) · "Run the full test suite in the background?" — Yes (Recommended) · No · Always this session.
   - **Large review only, same prompt:**
     - Graph: exists → Update it first, then review (Recommended) · Use as is (no update) · Ignore the graph (code only). None → Build it first (Recommended) · Code only. Runs on Opus via the knowledge-graph skill; the review starts after. Record the answer with knowledge-graph `update.py --choice now` (update) or `--choice skip` (use as is), so the end-of-task graph question is not repeated.
     - Related repos saved in the graph → "Include related repos?" Yes (Recommended) · No.
   - Change review: no setup graph question, no waiting — use the graph as it is.
1. Figure out what the change is supposed to do (PR description, commit message, or ask). Review against that goal.
2. Read the full diff, then the surrounding code: callers, callees, related tests, and how data flows in and out. Don't review lines in isolation.
   **Use the knowledge graph if `<repo>-knowledge-graph/` exists (or `./.knowledge-graph` points to one)** — as a map, not as the truth:
   - **Impact:** for each changed function, model, table, task, or config, walk the graph's edges to find everything that calls, reads, `ref()`s, or depends on it — then check those places in the code.
   - **Data model:** check the change against `data/model.json` — keys, grain, relationships, versioning. Flag changes that break a key, change a grain, or add a column/table the model doesn't know.
   - **Rules and flows:** check the change against the business rules and flows that cover it; flag where behaviour now differs.
   - **Code vs docs:** if the graph marks high-priority docs, flag changes that move the code further from them.
   - **Graph's `possible_issue` notes** ("noticed while mapping, not verified") for the files in scope: check each one — confirm it as a finding with a fix, or say it's not a problem.
   - **Cross-repo impact (if a `_combined` system graph exists, no question):** for a changed route, API contract, procedure, table, topic, or shared schema, list the callers in other repos that would break or change (`repo:path:line`), and flag them under Must/Should fix.
   - The diff is always judged on the **actual code**; the graph is from before the change. Where the graph is out of date for the files involved, read the code directly.
   - No graph: do the same by searching the code.
3. Tests as in the `darshan-singh-meel-code` skill (changed-code tests first; full suite per the step 0 answer), plus linter, type checker, and security tools on changed files. Say what ran (changed-only vs full).
4. Go through **every** section below (11 only if Yes in step 0; 12 Tech debt always). Skipping a section is fine only if it truly doesn't apply.
5. **End of a change review:** graph out of date for any files → the graph update question or the staleness note, as `update.py --dry-run` decides (knowledge-graph skill, "Keep it updated"). Otherwise nothing about the graph.

## 1. Correctness
- Trace the main path by hand. Does it actually do what it should?
- Edge cases: empty, null/None, zero, negative, boundary/off-by-one, duplicates, unicode, very large input.
- Error paths: handled or surfaced with a useful message? Anything swallowed silently?
- Bug fixes: root cause fixed, or symptom hidden (extra null check, broad try/except, retry, sleep)?
- State and concurrency: race conditions, shared mutable state, ordering assumptions, missing locks, non-atomic check-then-act.
- Resource handling: files, connections, locks, subprocesses closed/released on every path including errors.
- Types and units: implicit conversions, integer overflow, float comparisons, timezones, encodings.
- Breaking changes to public interfaces, APIs, file formats, or schemas — intended and called out?

## 2. Security
- **Injection:** user/external input reaching SQL, shell commands, eval, templates, file paths, regex, or HTML without parameterization/escaping.
- **Secrets:** hardcoded keys, tokens, passwords; secrets in logs, error messages, URLs, or committed config.
- **Auth:** missing or bypassable authentication/authorization checks; checks done client-side only; IDOR (accessing others' records by ID).
- **Input validation:** missing size/type/range limits; trusting client-supplied data, headers, or filenames.
- **Files & paths:** path traversal (`../`), unsafe temp files, overly broad permissions, unsafe deserialization (pickle, yaml.load, etc.).
- **Web:** XSS, CSRF, open redirects, SSRF (fetching user-supplied URLs), permissive CORS, missing security headers where relevant.
- **Crypto:** homemade crypto, weak hashing for passwords, non-cryptographic randomness for tokens.
- **Data exposure:** PII or sensitive data in logs, responses, or error traces.
- **Dependencies:** new packages that are unmaintained, unnecessary, or pulled from unusual sources.
- **Destructive operations** without confirmation, safeguards, or dry-run.

## 3. Performance
Flag only issues likely to matter at realistic scale — not micro-optimizations.
- Algorithmic: nested loops over large data (O(n²) where O(n) is easy), repeated linear searches that should be a set/dict lookup.
- **N+1 queries** and DB/API calls inside loops; missing batching.
- Missing indexes for new queries on large tables; unbounded queries with no limit/pagination.
- Repeated work: same computation, file read, or network call done multiple times when it could be done once.
- Loading entire large files/datasets into memory when streaming would do.
- Blocking I/O in async code or hot paths; unnecessary sync waits.
- Memory leaks: growing caches/lists without bounds, listeners never removed.
- Unnecessary copies of large structures; string concatenation in big loops.
- Don't suggest caching, parallelism, or clever optimizations without a clear, likely payoff.

## 4. Design
- Does the change fit the existing architecture and patterns, or introduce a second way of doing the same thing?
- Is logic in the right place (layer, module, class)? Business logic leaking into UI/handlers/DB code?
- Responsibilities clear? Functions/classes doing several unrelated things?
- Coupling: hidden dependencies, global state, tight coupling that makes testing hard.
- Duplication: copy-pasted logic that should reuse an existing function (but don't push abstraction for 2 near-copies).
- Naming: do names say what things are/do? Misleading names?
- Data modeling: right data structures and types? Stringly-typed values that should be enums/constants?
- API shape: easy to use correctly and hard to misuse? Confusing parameters, boolean flag arguments, inconsistent return types?

## 5. Complexity — too complicated?
- Could a junior developer understand this in one read? If not, why not?
- Deep nesting (3+ levels) → early returns / guard clauses.
- Long functions doing many things → split only where it clearly helps.
- Clever one-liners, dense comprehensions, metaprogramming, or magic that a plain loop would replace.
- Over-generalized code: generic frameworks, plugin systems, or config-driven behavior for a single use case.
- Indirection: wrappers around wrappers, factories, managers, interfaces with one implementation → inline.
- Show the simpler version when one exists.

## 6. Minimal size
- Could the same result be achieved with noticeably less code? Show the shorter version.
- Existing helper, standard-library function, or project utility that already does this?
- Speculative features, options, flags, or parameters nobody asked for → remove.
- Dead code, unused imports/variables/parameters → remove.
- New dependency where a few lines of code would do.
- Out-of-scope edits (reformatting, renames, drive-by refactors) → revert or split into separate change.

## 7. Verbosity & AI slop
- Comments/docstrings that restate the code or the function name.
- Chat leakage in comments, docstrings, commit/PR messages, docs, generated reports or UI copy: text addressed to the requester or recalling the chat ("updated as requested", "per user", "as discussed", "Claude added", "you haven't confirmed this on prod") → Should; Must if it misstates facts or exposes private chat content. Fix: state it as a fact about the system ("Not yet tested in production").
- Defensive checks for impossible cases; try/except around code that can't fail; redundant type checks.
- Excessive logging/prints; logging every step.
- Verbose variable names or explanations where short ones are clear; overly long error messages or boilerplate.
- TODOs, placeholders, "example usage" blocks, commented-out code.
- Unrequested README/summary/docs files.
- Overly formal or repetitive structure (same block copy-pasted with tiny changes).

## 8. Tests
- Is the change tested? Bug fix has a regression test that would have failed before?
- Missing high-value cases: main path, most likely edge case, error path, security-relevant inputs. Suggest only the **one to three** tests that add the most value.
- Bloat: near-identical tests → one parametrized test. Tests of framework/library/language → remove.
- Tests coupled to internals → test behavior instead. Over-mocking → mock only slow/external things.
- Flaky patterns: real time, sleeps, random data without seed, order dependence, network.
- **Red flags:** tests weakened, skipped, deleted, or code special-cased to make tests pass.

## 9. Obvious stuff (quick sweep)
- Typos in names, strings, user-facing text.
- Leftover debug code, hardcoded local paths, localhost URLs, test credentials.
- Wrong or missing return values; unreachable code; inverted conditions.
- Copy-paste errors (wrong variable in a duplicated block).
- Missing `await`, mutable default arguments, `==` vs `is`, etc. for the language in use.
- Config/env changes that will break other environments.
- Magic numbers that should be named constants.

## 10. Data stack (when SQL, dbt, Snowflake, Databricks, Airflow, or pipeline Python is in the diff)
The highest-value checks:
- **Grain & joins:** grain stated and correct? Any join that can fan out rows? `DISTINCT` hiding a bad join?
- **NULL traps:** `NOT IN` with nullable subquery, `LEFT JOIN` turned inner by a `WHERE` filter, `COUNT(col)` vs `COUNT(*)`.
- **Dedup:** `QUALIFY ROW_NUMBER()` with a deterministic order (tiebreaker)?
- **Idempotency:** rerunning the model/task/job for the same period gives the same result? Incremental logic handles late data and matches `--full-refresh`?
- **dbt:** `ref()`/`source()` used, right layer, PK `unique` + `not_null`, sensible materialization, no Jinja/macros for one-off SQL.
- **Snowflake:** pruning-friendly filters (no functions on filter columns), no `SELECT *` on wide tables, no admin roles, risky `CREATE OR REPLACE`.
- **Databricks/PySpark:** no `collect()`/`toPandas()`/row loops on big data, built-in functions over UDFs, sane partitioning, idempotent Delta writes.
- **Airflow:** no `datetime.now()` in task logic or `start_date`, no heavy top-level code or `Variable.get()` at parse time, no big data in XCom, sensors with timeout/reschedule, credentials via Connections.
- **ADF:** parameterised pipelines (not copies per table/env), managed identity / Key Vault for linked services, one window per run (idempotent), retries + failure alerts, deployed from Git/CI.
- **Versions:** code uses only features of the pinned versions; no deprecated syntax where a supported replacement exists.
- **Python pipelines:** no f-string SQL from external input, no `iterrows()` where vectorized works, heavy work pushed to the warehouse.
- **RBAC:** grants to roles/groups not users, least privilege, no admin roles in pipelines, service identities per pipeline, grants managed as code.
- **Terraform:** plan shows unexpected replace/destroy? `prevent_destroy` on stateful resources, pinned versions, no secrets in `.tf`; a committed `*.tfvars` is flagged by path, separate state per env.
- **Cloud storage:** no public access, encryption on, access via IAM role / managed identity (no keys), sensible prefix layout and lifecycle.
- **Cost:** will this scan far more data or burn more compute/credits than needed?
- **Tests:** follow `references/testing.md` in `darshan-singh-meel-data-platform` — PK tests and a check on the riskiest business rule, not a test on every column.

Tag these findings `[Data]`, or with the more specific area (e.g. `[Performance]`, `[Security]`).

## 11. Unused files (only if Yes in step 0)
Find files the repo doesn't need. **Never delete, move, or edit them — only mark them in the report.**

**What to look for**
- Code not imported, called, or referenced anywhere (modules, functions-only files, SQL files, macros, dbt models with no `ref()` and not exposed, DAGs not loaded, notebooks not used by jobs).
- Old copies and leftovers: `*_old`, `*_v1`, `*_backup`, `copy of …`, `.bak`, `tmp`, scratch scripts, commented-out-only files.
- `.md` / docs that describe things that no longer exist, duplicate another doc, or are empty/placeholder.
- Config, sample, or data files nothing reads; assets nothing links to.

**How**
- Use the knowledge graph if present (it's the best source here): nodes with no incoming `imports` / `calls` / `ref` / `reads` / `documents` edges. Otherwise search the repo for each file's name, module path, and table/model name.
- **Not unused, even with no references:** entry points (main scripts, DAG files, CLI, app start), tests, CI/CD and deploy files, migrations, IaC, `README`, `LICENSE`, `CLAUDE.md`, `.gitignore`, package/lock files, files loaded by name or pattern (glob, config lists, dynamic imports), and generated folders/files (`*-knowledge-graph/`, docs tagged `darshan-singh-meel-docs`) and git-ignored output (`reviews/`, `analysis/`) — those are outputs, not dead code. If unsure, mark **Check**, not Unused.

**Report** (terminal + HTML, own section after findings):
| File | Why it looks unused | Evidence | Confidence | Suggestion |
|---|---|---|---|---|
| `src/report_old.py` | Old copy of `report.py`; nothing imports it | no imports or references in repo or CI | High | Remove, or keep and note why |

- Confidence: **High** (no references, clearly old) · **Medium** (no references found, but could be loaded dynamically) · **Check** (owner should confirm).
- One line on impact: what removing them saves (clutter, confusion, build/scan time) and what keeping them costs. The user decides; nothing is deleted.

## 12. Tech debt (always)
Check the code in scope for debt, even when the change itself is fine:
- Workarounds and hacks; duplicated logic.
- Outdated, unpinned, or end-of-life versions; deprecated APIs.
- Missing tests on risky code.
- Hard-coded config or environment values.
- Dead or legacy paths kept alive; TODO/FIXME debt.
- Manual steps that should be automated.
- Schema or contract drift (code vs schema, docs, or callers).

Each finding tagged `[Tech debt]`: **what** · **cost of keeping it** (time, risk, money) · **fix** · **effort** (S/M/L). Severity: causes bugs, security, or data risk → Must; cost that grows → Should; else Other findings. Report real debt only, not every old line.

## Review discipline
- A committed secret file: flag it by path only, never open or quote it. The never-open rule covers scripts, grep, and scanners too: exclude those patterns; report path + rule name, value `<redacted>`.
- Thorough in checking, brief in reporting.
- The report may address the reader; it never quotes the chat.
- Every finding: `file:line` — what's wrong, why it matters, concrete fix (short snippet when helpful).
- Suggest the smallest fix. Don't rewrite the whole change.
- Don't invent problems to look thorough. If something is fine, don't mention it.
- Unsure? Put it under Questions, not findings.
- No praise padding, no summary of what the code does, no generic advice.
- Match the project's conventions; don't push personal style.

## Severity
- **Must fix:** bugs, security vulnerabilities, data loss risks (including tech debt that causes them), broken/gamed tests, unintended breaking changes, serious performance problems at realistic scale.
- **Should fix:** design problems, tech debt with growing cost, unnecessary complexity or code, out-of-scope edits, AI slop, missing key test, moderate performance issues.
- **Other findings:** optional, CLAUDE.md format (what · why · impact); only lower-impact items — anything with real risk goes under Must/Should fix.

## Output format
```
Verdict: Approve | Approve with changes | Request changes
Checks run: tests → result, linter → result | not run (why)
Tech debt: N items, biggest: <what> | none found

Must fix
- [Security] path/file.py:42 — <problem>. <why it matters>. Fix: <concrete fix>
- [Correctness] ...

Should fix
- [Complexity] path/file.py:88-120 — <problem>. Fix: <simpler version>
- [Performance] ...
- [Tech debt] path/file.py:8 — <what>. Cost: <time, risk, money>. Fix: <fix>. Effort: S | M | L

Questions
- ...

Unused files (table, section 11)

Areas checked with no issues: <e.g. Security, Performance>
Net size: <e.g. "could drop ~40 of the 65 added lines">

Other findings (only if any)
- [Obvious] path/file.py:12 — <what> · <why it matters> · <impact of fixing vs not>
```
Tag each finding with its area: Correctness, Security, Performance, Design, Complexity, Size, Slop, Tests, Obvious, Data, Tech debt.
Omit empty sections. If there are no findings, output the verdict, checks run, and "No issues found."

## HTML report (always)
- Show the review in the terminal **and** save it as one local, self-contained HTML file: `reviews/review-YYYY-MM-DD-HHMM.html` in the project root. Give the path.
- **Git-ignored by default:** git-ignore per CLAUDE.md. Commit reports only if the user asks; then remove the `/reviews/` line and say so. Already-tracked reports → tell the user once: `git rm -r --cached reviews/` stops tracking them (don't run it unasked).
- Same content as the terminal: verdict, checks run, findings grouped by severity, each tagged by area.
- Style per the `darshan-singh-meel-docs` skill (`references/html-style.md`): light, flat, printable, self-contained; works without JavaScript.
