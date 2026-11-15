# Report format

File: `reviews/darshan-singh-meel-snowflake-review-<YYYY-MM-DD-HHMM>.md`. Paths relative to the repo root. Addressed to the owner of the work; no quotes from the chat.

```markdown
# Snowflake review - <scope, relative path>

**Verdict:** Ready | Fix first | Rework
**Scope:** <files and questions reviewed> · **Checked against:** snowflake skill references, <docs pages opened>
**Counts:** Must <n> · Should <n> · Other <n>

## Must
1. **<file>:<line or cell N> - <short title>**
   - What: <the problem, with the quoted SQL fragment>.
   - Why: <the wrong number or risk it causes, with the reference entry or docs page>.
   - Fix: <the change, as SQL where useful>.

## Should
1. ... (same three lines)

## Other
- <file>:<line> - <one line each>

## Re-derived answers
| Question | Expected sources and grain | Work's sources and grain | Same answer? |
|---|---|---|---|

## Names checked
| Name | Used in | Status (ok / wrong / renamed / not verified) | Source |
|---|---|---|---|

## Script
`python <snowflake skill dir>/scripts/check_queries.py <folder>` → <n> ERROR, <n> WARN (each ERROR is listed above or explained here).

## Not checked
- <what could not be checked and why; the question that would settle it>
```

- Order findings by impact within each section.
- One finding per root cause; list the other places it occurs in the same finding.
- After a fix run: add `- Fixed: <what changed>` under each finding and update the verdict line.
