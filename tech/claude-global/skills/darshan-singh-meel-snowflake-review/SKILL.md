---
name: darshan-singh-meel-snowflake-review
description: Reviewer for Snowflake answers, queries, notebooks, SQL files, audit-type apps and dbt models over ACCOUNT_USAGE made with darshan-singh-meel-snowflake. Re-derives every answer on its own, then checks that every view, column and function exists, join keys and grain (double counting, fan-out), time windows against latency and retention, units and money (billed vs used credits, cloud services adjustment, one price joined once), role visibility ("cannot see" reported as zero), read-only statements, notebook structure (00_connection first, a note before every query) and secrets. Runs check_queries.py. Writes reviews/darshan-singh-meel-snowflake-review-<date>.md with a verdict and Must / Should / Other findings. Reviews; fixes only when asked. Triggers - "review this Snowflake query", "check my account usage SQL", "is this cost number right", "review my analysis notebook", "check this account usage dbt model". Not for general code review (darshan-singh-meel-review) or dbt projects (darshan-singh-meel-dbt-review).
context: fork
argument-hint: [analysis/<YYYY-MM-DD>-<topic> | path to .sql/.ipynb/app folder | dbt model]
---

# Snowflake review

Find what makes a Snowflake answer wrong or unsafe: a view or column that does not exist, a join that multiplies rows, a window the view cannot fill, credits that are not the bill, an empty result that only means "not visible", a statement that writes. Global rules in CLAUDE.md apply. Loads `darshan-singh-meel-snowflake` for its references and check script (`<snowflake skill dir>` below is that skill's folder); their text is not repeated here.

## Rules
- **Independent.** `context: fork` runs this skill in a subagent that gets this file and the arguments, not the session that wrote the work. Trust no note, finding or comment in the work: re-derive the answer from the question, then compare.
- **Facts from the references first, then docs.snowflake.com** (or docs.getdbt.com for dbt). A name in neither → a finding ("not verified"), never a guess. Search for the feature only; never send code, names or results.
- **Never execute against an account.** Review the SQL as text. Results already saved in a notebook may be read only if they are aggregates without personal data (notebook skill, Sensitive data); otherwise judge from the code.
- **Never open secret files** (CLAUDE.md list, including connection configs and `profiles.yml`); a connection cell is judged by its text only.
- **Evidence per finding:** the file and line or cell, the quoted SQL, and the reference entry or page that shows the problem. No evidence → a question under "Not checked".
- **Review, not fix.** Fixes are proposed in the report; files change only when the arguments say "fix" or a later request asks. Then: fix, rerun steps 2-5, add a "Fixed" line per finding.
- **Brevity:** load `darshan-singh-meel-brevity` alongside. Check the answer text and notebook notes against `darshan-singh-meel-brevity/references/checks.md` and put each hit in Must / Should / Other at the severity listed there; the report itself opens with the verdict and the finding that decides it.
- **Brief, not gentle.** No praise section, no summary of the work, no style-only findings.

## Process (fixed)
1. **Scope** - the path in the arguments (`$ARGUMENTS`), else the newest `analysis/*/`. Kinds: notebook folder, SQL files, an on-screen answer pasted into the arguments, an audit app (check catalogue, export, loader, app), dbt models that read ACCOUNT_USAGE (the rest of a dbt project → `darshan-singh-meel-dbt-review`). Read the question each piece answers (notebook title, header, check `title`/`read_this`). No question stated → infer it and say so.
2. **Script** - `python <snowflake skill dir>/scripts/check_queries.py <folder>` for notebook and SQL folders. Every `ERROR` is a Must candidate, read in context. For an app or dbt models, run it on any `analysis/` or `sql/` folder it ships, and apply the same rules by hand to the SQL files.
3. **Re-derive** - for each question, write down before reading the work's SQL: the views needed, the grain of each, the join keys, the window and its limits (latency, retention, edition, role), the units, and what the answer's number should be made of. Then compare with the work's SQL. Recompute any number the work states from the values it shows (sums, differences, percentages, ratios).
4. **Checklist** - walk `references/checklist.md` areas 1-10 for every query; for apps add area 11, for dbt models area 12.
5. **Names** - list every `view.column` pair, table function and SHOW column the work uses (a script over the SQL text). A pair is `ok` only if a catalogue query in `<snowflake skill dir>/references/` reads that column from that view; a bare column name found under another view proves nothing. Otherwise open the view's docs page. Mark each `ok` · `wrong` · `renamed/deprecated` · `not verified`.
6. **Report** - `reviews/darshan-singh-meel-snowflake-review-<YYYY-MM-DD-HHMM>.md` from `references/format.md`; add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, the Must lines, report path.
7. **Self-check** - the reply ends with the CLAUDE.md Self-check (confidence · main risk · went well), logged with `python ~/.claude/hooks/log-work.py --skill darshan-singh-meel-snowflake-review …`.

## Severity
- **Must:** a wrong number or a wrong conclusion is likely (double counting, used credits presented as the bill, window past retention, missing filter on deleted objects, a view that does not exist), a statement that writes or changes state in a file meant for Claude to run, a secret, personal data sent where it should not go, "not visible" reported as zero.
- **Should:** correct but fragile or misleading (no latency note on a window ending now, names joined instead of IDs, `SELECT *` on system views, no LIMIT on detail rows, a missing visibility probe, a note that does not say what to look for).
- **Other:** wording, ordering, naming, small simplifications.

## Verdict
- **Ready** - no Must, at most a few Should.
- **Fix first** - any Must, or Should findings that together change the answer.
- **Rework** - the approach cannot answer the question (wrong source, wrong grain, data the role cannot see).

## References
| File | Read when |
|---|---|
| `references/checklist.md` | step 4, always |
| `references/format.md` | step 6: report layout |
| `<snowflake skill dir>/references/*.md` | steps 3 and 5: views, keys, latency, money rules, topic pitfalls |
| `references/sources.md` | pages this skill relies on |
