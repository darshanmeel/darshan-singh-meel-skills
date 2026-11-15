# Report format

File: `reviews/databricks-review-<YYYY-MM-DD-HHMM>.md`. Paths relative to the repo root; secret values as `<redacted>`; no data rows.

```markdown
# Databricks review: <topic or artefact>

**Verdict:** Fail | Pass with fixes | Pass · Must <n> · Should <n> · Other <n>
**Scope:** <paths or "answer text">, <n> queries · check_queries.py: <n> FAIL

## Questions re-derived
| Question | Expected tables · keys · grain · window | Artefact matches? |
|---|---|---|
| <question> | <…> | yes / no (finding M1) |

## Must
- **M1 <short title>** (`<file>#cell N` or `<file>:line`, area <#>)
  - What: <the defect, with the quoted SQL>
  - Why: <the wrong number or risk it causes>
  - Fix: <corrected SQL or step>

## Should
- **S1 …** (same three lines)

## Other
- <one line each>

## Not checked
- <what could not be verified and how to check it, e.g. "check: <docs page>", or the read-only query to run>

## Fixed
- <only after a fix round: M1 fixed — <how>>
```
