---
name: darshan-singh-meel-snowflake-review
description: Reviewer for Snowflake answers, queries, notebooks, SQL files, audit-type apps and dbt models over ACCOUNT_USAGE made with darshan-singh-meel-snowflake. Re-derives every answer on its own, then checks that every view, column and function exists, join keys and grain (double counting, fan-out), time windows against latency and retention, units and money (billed vs used credits, cloud services adjustment, one price joined once), role visibility ("cannot see" reported as zero), read-only statements, notebook structure (00_connection first, a note before every query) and secrets. Runs check_queries.py. Writes reviews/darshan-singh-meel-snowflake-review-<date>.md with a verdict and Must / Should / Other findings. Reviews; fixes only when asked. Triggers - "review this Snowflake query", "check my account usage SQL", "is this cost number right", "review my analysis notebook", "check this account usage dbt model". Not for general code review (darshan-singh-meel-review) or dbt projects (darshan-singh-meel-dbt-review).
context: fork
argument-hint: [analysis/<YYYY-MM-DD>-<topic> | path to .sql/.ipynb/app folder | dbt model]
---

# Snowflake review
Find what makes a Snowflake answer wrong or unsafe: nonexistent view/column · join multiplying rows · window the view cannot fill · credits that are not the bill · empty result meaning only "not visible" · statement that writes. CLAUDE.md applies. Loads `darshan-singh-meel-snowflake` for references and check script (`<snowflake skill dir>` = its folder), not repeated here.

## Rules
- **Independent:** `context: fork` → subagent gets this file + arguments, not the writing session. Trust no note, finding or comment in the work: re-derive from the question, then compare.
- **Facts: references first → docs.snowflake.com** (docs.getdbt.com for dbt). Name in neither → finding "not verified", never a guess. Search the feature only; never send code, names or results.
- **Never execute against an account:** review SQL as text. Saved notebook results readable only if aggregates without personal data (notebook skill, Sensitive data); else judge from code.
- **Never open secret files** (CLAUDE.md list incl. connection configs, `profiles.yml`); connection cell judged by text only.
- **Evidence per finding:** file + line or cell · quoted SQL · reference entry or page showing the problem. No evidence → question under "Not checked".
- **Review, not fix:** fixes proposed in report; files change only when arguments say "fix" or a later request asks → fix · rerun steps 2-5 · "Fixed" line per finding.
- **Brief, not gentle:** no praise section · no summary of the work · no style-only findings.

## Process (fixed)
1. **Scope:** path in `$ARGUMENTS`, else newest `analysis/*/`. Kinds: notebook folder · SQL files · on-screen answer pasted in arguments · audit app (check catalogue, export, loader, app) · dbt models reading ACCOUNT_USAGE (rest of a dbt project → `darshan-singh-meel-dbt-review`). Read the question each piece answers (notebook title, header, check `title`/`read_this`). None stated → infer, say so.
2. **Script:** `python <snowflake skill dir>/scripts/check_queries.py <folder>` for notebook and SQL folders. Every `ERROR` = Must candidate, read in context. App or dbt models → run on any `analysis/` or `sql/` folder shipped; same rules by hand on the SQL files.
3. **Re-derive:** per question, before reading the work's SQL, write: views needed · grain of each · join keys · window and limits (latency, retention, edition, role) · units · what the number is made of. Then compare with the work's SQL. Recompute every stated number from shown values (sums, differences, percentages, ratios).
4. **Checklist:** `references/checklist.md` areas 1-10 per query · apps add 11 · dbt models add 12.
5. **Names:** list every `view.column` pair, table function and SHOW column used (script over the SQL text). `ok` only if a catalogue query in `<snowflake skill dir>/references/` reads that column from that view; a bare column name under another view proves nothing. Else open the view's docs page. Mark `ok` · `wrong` · `renamed/deprecated` · `not verified`.
6. **Report:** `reviews/darshan-singh-meel-snowflake-review-<YYYY-MM-DD-HHMM>.md` per `references/format.md`; folder first created → add `/reviews/` to `.gitignore`. Reply: verdict · counts · Must lines · report path.
7. **Self-check:** reply ends with CLAUDE.md Self-check (confidence · main risk · went well), logged with `python ~/.claude/hooks/log-work.py --skill darshan-singh-meel-snowflake-review …`.

## Severity
- **Must:** wrong number or conclusion likely (double counting · used credits as the bill · window past retention · missing filter on deleted objects · nonexistent view) · statement that writes or changes state in a file meant for Claude to run · secret · personal data sent where it should not go · "not visible" reported as zero.
- **Should:** correct but fragile or misleading (no latency note on a window ending now · names joined instead of IDs · `SELECT *` on system views · no LIMIT on detail rows · missing visibility probe · note not saying what to look for).
- **Other:** wording · ordering · naming · small simplifications.

## Verdict
- **Ready:** no Must, at most a few Should.
- **Fix first:** any Must, or Should findings that together change the answer.
- **Rework:** approach cannot answer the question (wrong source · wrong grain · data the role cannot see).

## References
| File | Read when |
|---|---|
| `references/checklist.md` | step 4, always |
| `references/format.md` | step 6: report layout |
| `<snowflake skill dir>/references/*.md` | steps 3 and 5: views, keys, latency, money rules, topic pitfalls |
| `references/sources.md` | pages this skill relies on |
